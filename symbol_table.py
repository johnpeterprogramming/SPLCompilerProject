"""
SPL Symbol Table
COS341 Semester Project 2025

Symbol table implementation for static semantic checking.
Uses a dictionary-based approach with node IDs as keys.
"""

from typing import Dict, List, Optional, Set
from enum import Enum


class SymbolType(Enum):
    """Type of symbol in the symbol table"""
    VARIABLE = "variable"
    PROCEDURE = "procedure"
    FUNCTION = "function"


class ScopeType(Enum):
    """Scope type for symbols"""
    EVERYWHERE = "everywhere"
    GLOBAL = "global"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    MAIN = "main"
    LOCAL = "local"  # local scope within a procedure or function


class SymbolEntry:
    """Represents an entry in the symbol table"""
    
    def __init__(self, node_id: int, name: str, symbol_type: SymbolType, 
                 scope: ScopeType, declaration_node_id: int, 
                 parent_scope_id: Optional[int] = None):
        self.node_id = node_id
        self.name = name
        self.symbol_type = symbol_type
        self.scope = scope
        self.declaration_node_id = declaration_node_id
        self.parent_scope_id = parent_scope_id  # For local scopes
    
    def __str__(self):
        return (f"SymbolEntry(node_id={self.node_id}, name='{self.name}', "
                f"type={self.symbol_type.value}, scope={self.scope.value})")
    
    def __repr__(self):
        return self.__str__()


class SymbolTable:
    """Symbol table for SPL static semantic checking"""
    
    def __init__(self):
        # Main storage: node_id -> SymbolEntry
        self.symbols: Dict[int, SymbolEntry] = {}
        
        # Index by name for quick lookup
        self.by_name: Dict[str, List[SymbolEntry]] = {}
        
        # Index by scope for quick scope-based queries
        self.by_scope: Dict[ScopeType, List[SymbolEntry]] = {
            scope: [] for scope in ScopeType
        }
    
    def add_symbol(self, node_id: int, name: str, symbol_type: SymbolType,
                   scope: ScopeType, declaration_node_id: int,
                   parent_scope_id: Optional[int] = None) -> SymbolEntry:
        """Add a symbol to the table"""
        entry = SymbolEntry(node_id, name, symbol_type, scope, 
                          declaration_node_id, parent_scope_id)
        
        # Add to main storage
        self.symbols[node_id] = entry
        
        # Add to name index
        if name not in self.by_name:
            self.by_name[name] = []
        self.by_name[name].append(entry)
        
        # Add to scope index
        self.by_scope[scope].append(entry)
        
        return entry
    
    def lookup(self, node_id: int) -> Optional[SymbolEntry]:
        """Look up a symbol by node ID"""
        return self.symbols.get(node_id)
    
    def lookup_by_name(self, name: str) -> List[SymbolEntry]:
        """Look up all symbols with a given name"""
        return self.by_name.get(name, [])
    
    def get_symbols_in_scope(self, scope: ScopeType) -> List[SymbolEntry]:
        """Get all symbols in a specific scope"""
        return self.by_scope[scope]
    
    def check_duplicate_in_scope(self, name: str, scope: ScopeType, 
                                 parent_scope_id: Optional[int] = None) -> Optional[SymbolEntry]:
        """
        Check if a name already exists in a specific scope.
        Returns the existing entry if found, None otherwise.
        """
        for entry in self.by_scope[scope]:
            if entry.name == name:
                # For local scopes, also check parent scope ID
                if scope == ScopeType.LOCAL:
                    if entry.parent_scope_id == parent_scope_id:
                        return entry
                else:
                    return entry
        return None
    
    def check_duplicate_in_everywhere_scope(self, name: str, 
                                           exclude_type: Optional[SymbolType] = None) -> Optional[SymbolEntry]:
        """
        Check if a name conflicts with other names in the Everywhere scope.
        Returns the conflicting entry if found, None otherwise.
        exclude_type allows checking for conflicts with other types only.
        """
        for entry in self.by_name.get(name, []):
            if entry.scope in [ScopeType.GLOBAL, ScopeType.PROCEDURE, ScopeType.FUNCTION]:
                if exclude_type is None or entry.symbol_type != exclude_type:
                    return entry
        return None
    
    def get_local_scope_symbols(self, parent_scope_id: int) -> List[SymbolEntry]:
        """Get all symbols in a specific local scope (by parent scope ID)"""
        return [entry for entry in self.by_scope[ScopeType.LOCAL] 
                if entry.parent_scope_id == parent_scope_id]
    
    def update_symbol_reference(self, node_id: int, declaration_node_id: int):
        """Update a symbol to reference its declaration"""
        if node_id in self.symbols:
            self.symbols[node_id].declaration_node_id = declaration_node_id
    
    def print_table(self):
        """Print the symbol table in a readable format"""
        print("\n=== Symbol Table ===")
        print(f"{'Node ID':<10} {'Name':<20} {'Type':<12} {'Scope':<15} {'Decl ID':<10}")
        print("-" * 70)
        
        for node_id in sorted(self.symbols.keys()):
            entry = self.symbols[node_id]
            print(f"{entry.node_id:<10} {entry.name:<20} {entry.symbol_type.value:<12} "
                  f"{entry.scope.value:<15} {entry.declaration_node_id:<10}")
        
        print("-" * 70)
        print(f"Total symbols: {len(self.symbols)}\n")
    
    def get_summary(self) -> str:
        """Get a summary of the symbol table"""
        summary = []
        summary.append(f"Total symbols: {len(self.symbols)}")
        
        # Count by type
        type_counts = {}
        for entry in self.symbols.values():
            type_name = entry.symbol_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        for type_name, count in sorted(type_counts.items()):
            summary.append(f"  {type_name}s: {count}")
        
        return "\n".join(summary)


