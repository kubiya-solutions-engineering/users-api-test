from kubiya_sdk.tools.models import Tool, FileSpec

USER_API_ICON = "https://cdn-icons-png.flaticon.com/512/1077/1077114.png"

class UserApiTool(Tool):
    def __init__(self, name, description, content, args, long_running=False, mermaid_diagram=None):
        # Kubernetes context injection script
        inject_kubernetes_context = """#!/bin/bash
set -eu
TOKEN_LOCATION="/tmp/kubernetes_context_token"
CERT_LOCATION="/tmp/kubernetes_context_cert"
# Inject in-cluster context using the temporary token file
if [ -f $TOKEN_LOCATION ] && [ -f $CERT_LOCATION ]; then
    KUBE_TOKEN=$(cat $TOKEN_LOCATION)
    kubectl config set-cluster in-cluster --server=https://kubernetes.default.svc \
                                          --certificate-authority=$CERT_LOCATION > /dev/null 2>&1
    kubectl config set-credentials in-cluster --token=$KUBE_TOKEN > /dev/null 2>&1
    kubectl config set-context in-cluster --cluster=in-cluster --user=in-cluster > /dev/null 2>&1
    kubectl config use-context in-cluster > /dev/null 2>&1
else
    echo "Error: Kubernetes context token or cert file not found at $TOKEN_LOCATION \
          or $CERT_LOCATION respectively."
    exit 1
fi

"""
        # Create argument passing section
        arg_names = [arg.name for arg in args]
        arg_vars = ", ".join(f'"${{{name}}}"' for name in arg_names)
        
        # Pass arguments directly to Python script
        inject_kubernetes_context += f"\n# Execute the Python script with arguments\npython3 << EOF\n"
        inject_kubernetes_context += "import sys\n"
        inject_kubernetes_context += f"args = [{arg_vars}]\n"
        
        script_footer = "\nEOF"
        full_content = f"{inject_kubernetes_context}\n{content}{script_footer}"

        # Define Kubernetes file specifications
        file_specs = [
            FileSpec(
                source="/var/run/secrets/kubernetes.io/serviceaccount/token",
                destination="/tmp/kubernetes_context_token"
            ),
            FileSpec(
                source="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
                destination="/tmp/kubernetes_context_cert"
            )
        ]

        super().__init__(
            name=name,
            description=description,
            icon_url=USER_API_ICON,
            type="docker",
            image="michaelkubiya/python-kube:latest",
            content=full_content,
            args=args,
            requirements=["requests"],
            long_running=long_running,
            mermaid=mermaid_diagram,
            with_files=file_specs,
        )