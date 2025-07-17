#!/usr/bin/env python
import sys
import dotenv
from prometheus_mcp_server.server import mcp, config
from prometheus_mcp_server.logging_config import setup_logging, get_logger

# Initialize structured logging
logger = setup_logging()

def setup_environment():
    if dotenv.load_dotenv():
        logger.info("Environment configuration loaded", source=".env file")
    else:
        logger.info("Environment configuration loaded", source="environment variables", note="No .env file found")

    # Validate tenant configuration
    if not config.tenants:
        logger.error(
            "Missing required configuration",
            error="No tenants configured",
            suggestion="Please set either PROMETHEUS_URL (single tenant) or PROMETHEUS_TENANTS (multi-tenant) environment variable"
        )
        return False
    
    # Log tenant configuration summary
    tenant_summary = []
    for tenant in config.tenants:
        auth_method = "none"
        if tenant.username and tenant.password:
            auth_method = "basic_auth"
        elif tenant.token:
            auth_method = "bearer_token"
        
        tenant_summary.append({
            "name": tenant.name,
            "url": tenant.url,
            "authentication": auth_method,
            "org_id": tenant.org_id if tenant.org_id else None
        })
    
    logger.info(
        "Multi-tenant Prometheus configuration validated",
        tenant_count=len(config.tenants),
        default_tenant=config.default_tenant,
        tenants=tenant_summary
    )
    
    return True

def run_server():
    """Main entry point for the Prometheus MCP Server"""
    # Setup environment
    try:
        if not setup_environment():
            logger.error("Environment setup failed, exiting")
            sys.exit(1)
    except Exception as e:
        logger.error("Failed to load configuration", error=str(e), error_type=type(e).__name__)
        sys.exit(1)
    
    logger.info("Starting Prometheus MCP Server", 
               transport="stdio", 
               tenant_count=len(config.tenants),
               default_tenant=config.default_tenant)
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
