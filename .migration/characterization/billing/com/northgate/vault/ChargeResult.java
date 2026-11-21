package com.northgate.vault;

public record ChargeResult(boolean approved, String reason, String reference) {
}
