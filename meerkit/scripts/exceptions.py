from meerkit.exceptions import MeerkitError


class ScriptError(MeerkitError):
    default_error_code = "script_error"
    default_status_code = 500
    default_retryable = False


class BackfillScriptError(ScriptError):
    default_error_code = "backfill_script_error"


class DiffRecordNotFoundError(BackfillScriptError):
    default_error_code = "diff_record_not_found"


class ScriptFileNotFoundError(BackfillScriptError):
    default_error_code = "script_file_not_found"


class ScriptDataParseError(BackfillScriptError):
    default_error_code = "script_data_parse_error"


class ScanScriptError(ScriptError):
    default_error_code = "scan_script_error"


class ScanCredentialsError(ScanScriptError):
    default_error_code = "scan_credentials_error"
