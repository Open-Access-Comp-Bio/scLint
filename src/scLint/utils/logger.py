class Issue:
    def __init__(self, message, severity="ERROR", source=None):
        self.message = message
        self.severity = severity.upper()
        self.source = source

    def __repr__(self):
        return (
            f"Issue(severity='{self.severity}', "
            f"source='{self.source}', message='{self.message}')"
        )

    def __str__(self):
        """
        User-friendly string for display.
        Example: [ERROR] (check_obs): Missing 'cell_type' in adata.obs
        """
        parts = [f"[{self.severity}]"]
        if self.source:
            parts.append(f"({self.source})")
        parts.append(self.message)
        return " ".join(parts)

    def is_error(self):
        return self.severity == "ERROR"

    def is_warning(self):
        return self.severity == "WARNING"