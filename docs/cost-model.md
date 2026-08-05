# Cost model

The local control plane has no cloud cost. The optional evidence baseline uses
managed identity, Log Analytics, and geo-redundant Storage; target-service costs
depend on AKS, Key Vault, Secrets Store CSI Driver, Managed Identity. Before deployment, price the selected
region, estimate fixed and per-operation charges, set a resource-group budget,
cap log retention and daily ingestion, and define an automatic stop threshold.

`deployPlatform=false` is the safe default. This repository includes no price
claim because Azure prices, licensing, quotas, and regional availability change.
