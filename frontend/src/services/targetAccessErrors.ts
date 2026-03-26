function toLower(value: string | null | undefined): string {
    return (value || "").trim().toLowerCase();
}

function isAccountDeactivatedMessage(message: string): boolean {
    return (
        message.includes("deactivated") ||
        message.includes("disabled") ||
        message.includes("does not exist") ||
        message.includes("doesn't exist") ||
        message.includes("not found") ||
        message.includes("no longer available")
    );
}

function isProfileInaccessibleMessage(message: string): boolean {
    return (
        message.includes("could not load this target") ||
        message.includes("could not load target") ||
        message.includes("unable to load") ||
        message.includes("failed to load") ||
        message.includes("inaccessible") ||
        message.includes("private") ||
        message.includes("not authorized") ||
        message.includes("forbidden") ||
        message.includes("'nonetype' object is not subscriptable") ||
        message.includes('"nonetype" object is not subscriptable') ||
        message.includes("nonetype object is not subscriptable")
    );
}

export function extractApiErrorMessage(error: unknown): string | null {
    const maybeMessage = (error as { response?: { data?: { error?: string } } })
        ?.response?.data?.error;
    if (typeof maybeMessage === "string" && maybeMessage.trim()) {
        return maybeMessage.trim();
    }
    return null;
}

export function mapTargetAccessError(
    errorMessage: string | null,
    fallbackMessage: string,
): string {
    const normalized = toLower(errorMessage);
    if (!normalized) {
        return fallbackMessage;
    }
    if (isAccountDeactivatedMessage(normalized)) {
        return "Account deactivated";
    }
    if (isProfileInaccessibleMessage(normalized)) {
        return "Profile inaccessible";
    }
    return errorMessage || fallbackMessage;
}
