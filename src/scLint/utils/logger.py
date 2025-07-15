import datetime


class Issue:
    """
    Represents a linting issue detected during validation of an AnnData object.

    Attributes:
        message (str): Description of the issue.
        severity (str): Severity level ("ERROR" or "WARNING"). Defaults to "ERROR".
        source (str, optional): Optional identifier for the source of the issue (e.g., function name).
    """
    def __init__(self, message, severity="ERROR", source=None):
        """
        Initialize an Issue object.

        Parameters:
            message (str): Description of the issue.
            severity (str): Severity level. Either "ERROR" or "WARNING". Defaults to "ERROR".
            source (str, optional): Identifier for the source that raised the issue.
        """
        self.message = message
        self.severity = severity.upper()
        self.source = source

    def __repr__(self):
        """
        Return a formal string representation of the issue.
        """
        return (
            f"Issue(severity='{self.severity}', "
            f"source='{self.source}', message='{self.message}')"
        )

    def __str__(self):
        """
        Return a user-friendly string describing the issue.
        """
        parts = [f"[{self.severity}]"]
        if self.source:
            parts.append(f"({self.source})")
        parts.append(self.message)
        return " ".join(parts)

    def is_error(self):
        """
        Check if the issue is an error.

        Returns:
            bool: True if severity is "ERROR", else False.
        """
        return self.severity == "ERROR"

    def is_warning(self):
        """
        Check if the issue is a warning.

        Returns:
            bool: True if severity is "WARNING", else False.
        """
        return self.severity == "WARNING"


class Logger:
    """
    Logger for collecting, printing, and saving issues and messages during linting.

    Attributes:
        verbose (bool): Whether to print messages to stdout.
        log_file (str): Optional path to a file where logs will be saved.
        issues (List[Issue]): Accumulated list of Issue instances.
    """
    def __init__(self, verbose=True, log_file=None):
        """
        Initialize the Logger.

        Parameters:
            verbose (bool): Whether to print log messages to the console. Defaults to True.
            log_file (str, optional): Path to file for saving logs. If None, logging is console-only.
        """
        self.verbose = verbose
        self.log_file = log_file
        self.issues = []

        if log_file:
            with open(log_file, "w") as f:
                f.write(f"Log started at {datetime.datetime.now()}\n")

    def log(self, message, severity="INFO", source=None):
        """
        Log a message to console and/or file.

        Parameters:
            message (str): The message to log.
            severity (str): Message severity ("INFO", "ERROR", "WARNING").
            source (str, optional): Identifier of the source function or component.
        """
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
        """
        Add an Issue to the logger and log it immediately.

        Parameters:
            issue (Issue): The Issue instance to record.

        Raises:
            TypeError: If the provided argument is not an instance of Issue.
        """
        if not isinstance(issue, Issue):
            raise TypeError("Only Issue instances can be recorded.")
        self.issues.append(issue)
        self.log(str(issue), severity=issue.severity, source=issue.source)

    def summary(self):
        """
        Print a summary of all recorded issues (counts and details).
        """
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
        """
        Check if any recorded issues are errors.

        Returns:
            bool: True if at least one issue is an error.
        """
        return any(i.is_error() for i in self.issues)

    def clear(self):
        """
        Clear all recorded issues from the logger.
        """
        self.issues.clear()
