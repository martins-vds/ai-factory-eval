package com.northgate.vault;

public final class ChargeResult {
    private final boolean approved;
    private final String reference;
    private final String reason;

    public ChargeResult(boolean approved, String reference, String reason) {
        this.approved = approved;
        this.reference = reference;
        this.reason = reason;
    }

    public boolean approved() {
        return approved;
    }

    public String reference() {
        return reference;
    }

    public String reason() {
        return reason;
    }
}
