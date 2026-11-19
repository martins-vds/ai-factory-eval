package com.northgate.vault;

public record ChargeResult(boolean approved, String reference, String reason) {
}
