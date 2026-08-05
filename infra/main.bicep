targetScope = 'resourceGroup'

@description('Safe default: create no chargeable Azure resources until explicitly enabled.')
param deployPlatform bool = false
param location string = resourceGroup().location
@minLength(3)
@maxLength(12)
param namePrefix string = 'mvpref'

var suffix = uniqueString(resourceGroup().id)
var identityName = '${namePrefix}-id-${suffix}'
var workspaceName = '${namePrefix}-log-${suffix}'
var storageName = take(toLower(replace('${namePrefix}${suffix}', '-', '')), 24)

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = if (deployPlatform) {
  name: identityName
  location: location
  tags: { purpose: 'reference-evidence' }
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = if (deployPlatform) {
  name: workspaceName
  location: location
  properties: {
    retentionInDays: 30
    features: { enableLogAccessUsingOnlyResourcePermissions: true }
    publicNetworkAccessForIngestion: 'Disabled'
    publicNetworkAccessForQuery: 'Disabled'
  }
}

resource evidence 'Microsoft.Storage/storageAccounts@2023-05-01' = if (deployPlatform) {
  name: storageName
  location: location
  sku: { name: 'Standard_GRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Disabled'
    supportsHttpsTrafficOnly: true
    encryption: {
      keySource: 'Microsoft.Storage'
      requireInfrastructureEncryption: true
      services: { blob: { enabled: true } }
    }
  }
}

output managedIdentityResourceId string = deployPlatform ? identity.id : ''
output evidenceStorageResourceId string = deployPlatform ? evidence.id : ''
output logWorkspaceResourceId string = deployPlatform ? workspace.id : ''
