# Ansible Workflow Diagram

```mermaid
graph TB
    classDef configFile fill:#7D3C98,color:#fff,stroke:#333,stroke-width:2px;
    classDef playbook fill:#2980B9,color:#fff,stroke:#333,stroke-width:2px;
    classDef role fill:#27AE60,color:#fff,stroke:#333,stroke-width:2px;
    classDef task fill:#C0392B,color:#fff,stroke:#333,stroke-width:2px;
    classDef verify fill:#E67E22,color:#fff,stroke:#333,stroke-width:2px;
    classDef script fill:#F1C40F,color:#333,stroke:#333,stroke-width:2px;

    subgraph Configuration
        O[group_vars/all.yml]:::configFile
        P[roles/local/defaults/main.yml]:::configFile
        Q[inventory/staging]:::configFile
        R[inventory/production]:::configFile
    end

    subgraph Scripts
        S[run-staging.sh]:::script
        T[run-production.sh]:::script
    end

    subgraph Main Playbooks
        A[main.yml]:::playbook
        B[dev-cleanup.yml]:::playbook
    end

    subgraph Pre-Tasks
        PreC[pre_checks.yml]:::task
        DNS[dns.yml]:::task
    end

    subgraph External Roles
        D[elliotweiser.osx-command-line-tools]:::role
        E[geerlingguy.mac.homebrew]:::role
    end

    subgraph Local Role Tasks
        subgraph Development
            H[node.yml]:::task
            I[pyenv.yml]:::task
        end

        subgraph Network
            J[tailscale.yml]:::task
        end
    end

    subgraph Verification
        V[verify.yml]:::verify
    end

    S --> A
    T --> A
    O & P --> A
    Q --> S
    R --> T

    A --> PreC
    PreC --> D
    D --> E
    E --> H & I & J
    J --> DNS

    H & I & J --> V
    DNS --> V

    B -.-> V
```

## Workflow Explanation

1. **Entry Points**:

   - Production deployment via `run-production.sh`
   - Staging deployment via `run-staging.sh`
   - Development cleanup via `dev-cleanup.yml`

2. **Configuration Files**:

   - `group_vars/all.yml`: Environment-specific configurations
   - `roles/local/defaults/main.yml`: Default role configurations
   - `inventory/staging` & `inventory/production`: Host definitions

3. **Pre-flight Checks**:

   - System requirements verification
   - Directory structure setup
   - Network connectivity tests

4. **External Roles**:

   - Command Line Tools installation
   - Homebrew package management

5. **Local Role Tasks**:

   - **Development**:
     - Node.js setup with NVM
     - Python environment with pyenv
   - **Network**:
     - Tailscale configuration
     - DNS management

6. **Verification**:
   - Installation checks
   - Service status verification
   - Configuration validation

## Color Legend

- 🟣 Configuration Files (Purple)
- 🔵 Playbooks (Blue)
- 🟢 Roles (Green)
- 🔴 Tasks (Red)
- 🟠 Verification (Orange)
- 🟡 Scripts (Yellow)
