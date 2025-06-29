from pydantic import BaseModel


class BytecodeAnalysisResult(BaseModel):
    """
    Represents the complete analysis result of a smart contract including
    runtime bytecode, creation bytecode, and constructor arguments.

    Attributes:
        runtime_bytecode: The deployed bytecode stored on the blockchain
        creation_bytecode: The creation transaction input data
        constructor_args: Extracted constructor arguments (if available)
        errors: List of any errors encountered during extraction
    """

    runtime_bytecode: str = ""
    creation_bytecode: str = ""
    constructor_args: str = ""
    errors: list[str] = []

    class Config:
        """Pydantic configuration"""

        frozen = False  # Allow modification after creation
        validate_assignment = True  # Validate values when assigned

    def has_errors(self) -> bool:
        """Check if there were any errors during the analysis."""
        return len(self.errors) > 0

    def has_runtime_bytecode(self) -> bool:
        """Check if runtime bytecode was successfully retrieved."""
        return bool(self.runtime_bytecode and self.runtime_bytecode != "0x")

    def has_creation_bytecode(self) -> bool:
        """Check if creation bytecode was successfully retrieved."""
        return bool(self.creation_bytecode and self.creation_bytecode != "0x")

    def has_constructor_args(self) -> bool:
        """Check if constructor arguments were successfully extracted."""
        return bool(self.constructor_args and self.constructor_args != "0x")

    def is_complete_analysis(self) -> bool:
        """Check if the analysis is complete (has all components without errors)."""
        return (
            self.has_runtime_bytecode()
            and self.has_creation_bytecode()
            and not self.has_errors()
        )

    def summary(self) -> str:
        """Get a summary of the analysis results."""
        parts = []
        if self.has_runtime_bytecode():
            parts.append("✓ Runtime bytecode")
        else:
            parts.append("✗ Runtime bytecode")

        if self.has_creation_bytecode():
            parts.append("✓ Creation bytecode")
        else:
            parts.append("✗ Creation bytecode")

        if self.has_constructor_args():
            parts.append("✓ Constructor args")
        else:
            parts.append("✗ Constructor args")

        if self.has_errors():
            parts.append(f"⚠ {len(self.errors)} errors")

        return " | ".join(parts)
