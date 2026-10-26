terraform {
  required_version = ">= 1.9, < 2.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
  backend "azurerm" {
    use_azuread_auth = true
  }
}
provider "azurerm" {
  features {}
}
variable "prefix" {
  type        = string
  description = "3-12 lowercase letters or digits; used in resource names."
  validation {
    condition     = can(regex("^[a-z][a-z0-9]{2,11}$", var.prefix))
    error_message = "Use 3-12 lowercase letters/digits, starting with a letter."
  }
}
variable "location" {
  type    = string
  default = "eastus2"
}
variable "deployer_object_id" {
  type        = string
  description = "Entra service principal OBJECT ID for GitHub OIDC, not its client ID."
}
variable "node_size" {
  type    = string
  default = "Standard_D2s_v5"
}
resource "azurerm_resource_group" "platform" {
  name     = "rg-${var.prefix}-platformops"
  location = var.location
  tags     = { project = "platformops-board", environment = "lab", owner = "rakesh-goriga" }
}
resource "azurerm_container_registry" "images" {
  name                = "${var.prefix}platformops"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  sku                 = "Basic"
  admin_enabled       = false
}
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "law-${var.prefix}-platformops"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}
resource "azurerm_kubernetes_cluster" "platform" {
  name                = "aks-${var.prefix}-platformops"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  dns_prefix          = "${var.prefix}-platformops"
  sku_tier            = "Free"
  local_account_disabled = true
  oidc_issuer_enabled     = true
  workload_identity_enabled = true
  default_node_pool {
    name                 = "system"
    vm_size              = var.node_size
    node_count           = 2
    auto_scaling_enabled = true
    min_count            = 2
    max_count            = 3
    os_disk_size_gb      = 64
    upgrade_settings {
      max_surge = "33%"
    }
  }
  identity {
    type = "SystemAssigned"
  }
  azure_active_directory_role_based_access_control {
    azure_rbac_enabled = true
  }
  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    network_policy      = "azure"
    pod_cidr            = "10.244.0.0/16"
    service_cidr        = "10.2.0.0/16"
    dns_service_ip      = "10.2.0.10"
    load_balancer_sku   = "standard"
  }
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
  }
}
resource "azurerm_role_assignment" "image_pull" {
  scope                = azurerm_container_registry.images.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.platform.kubelet_identity[0].object_id
  skip_service_principal_aad_check = true
}
resource "azurerm_role_assignment" "image_push" {
  scope                = azurerm_container_registry.images.id
  role_definition_name = "AcrPush"
  principal_id         = var.deployer_object_id
}
resource "azurerm_role_assignment" "cluster_user" {
  scope                = azurerm_kubernetes_cluster.platform.id
  role_definition_name = "Azure Kubernetes Service Cluster User Role"
  principal_id         = var.deployer_object_id
}
resource "azurerm_role_assignment" "cluster_admin" {
  scope                = azurerm_kubernetes_cluster.platform.id
  role_definition_name = "Azure Kubernetes Service RBAC Cluster Admin"
  principal_id         = var.deployer_object_id
}
output "resource_group" { value = azurerm_resource_group.platform.name }
output "cluster_name" { value = azurerm_kubernetes_cluster.platform.name }
output "registry_name" { value = azurerm_container_registry.images.name }
output "registry_server" { value = azurerm_container_registry.images.login_server }
