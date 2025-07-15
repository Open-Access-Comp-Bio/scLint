import datetime


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
        parts = [f"[{self.severity}]"]
        if self.source:
            parts.append(f"({self.source})")
        parts.append(self.message)
        return " ".join(parts)

    def is_error(self):
        return self.severity == "ERROR"

    def is_warning(self):
        return self.severity == "WARNING"


class Logger:
    def __init__(self, verbose=True, log_file=None):
        self.verbose = verbose
        self.log_file = log_file
        self.issues = []

        if log_file:
            with open(log_file, "w") as f:
                f.write(f"Log started at {datetime.datetime.now()}\n")

    def log(self, message, severity="INFO", source=None):
        msg = f"[{severity.upper()}]"
        if source:
            msg += f" ({source})"
        msg += f" {message}"

        if self.verbose:
            print(msg)

        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(msg + "\n")

    def record_issue(self, issue):
        if not isinstance(issue, Issue):
            raise TypeError("Only Issue instances can be recorded.")
        self.issues.append(issue)
        self.log(str(issue), severity=issue.severity, source=issue.source)

    def summary(self):
        errors = sum(1 for i in self.issues if i.is_error())
        warnings = sum(1 for i in self.issues if i.is_warning())

        summary_msg = (
            f"\n Linting complete: {len(self.issues)} issue(s) found\n"
            f"   {errors} error(s)\n"
            f"   {warnings} warning(s)\n"
        )
        self.log(summary_msg.strip(), severity="INFO")

        for issue in self.issues:
            self.log(str(issue), severity=issue.severity)

    def has_errors(self):
        return any(i.is_error() for i in self.issues)

    def clear(self):
        self.issues.clear()
