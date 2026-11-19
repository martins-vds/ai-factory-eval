package com.northgate.vault;

public final class ChargeResult {
    private final boolean approved;
    private final String reason;
    private final String reference;

    public ChargeResult(boolean approved, String reason, String reference) {
        this.approved = approved;
        this.reason = reason;
        this.reference = reference;
    }

    public boolean approved() {
        return approved;
    }

    public String reason() {
        return reason;
    }

    public String reference() {
        return reference;
    }
}
