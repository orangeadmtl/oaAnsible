# Ansible Workflow Diagram

```mermaid
graph LR
    classDef configFile fill:#7D3C98,color:#fff,stroke:#333,stroke-width:2px;
    classDef playbook fill:#2980B9,color:#fff,stroke:#333,stroke-width:2px;
    classDef role fill:#27AE60,color:#fff,stroke:#333,stroke-width:2px;
    classDef task fill:#C0392B,color:#fff,stroke:#333,stroke-width:2px;
    classDef handlers fill:#8E44AD,color:#fff,stroke:#333,stroke-width:2px;

    subgraph Configuration
        O[default.config.yml]:::configFile
        P[config.yml]:::configFile
        Q[inventory]:::configFile
    end

    subgraph Main Playbook
        A[main.yml]:::playbook
    end

    subgraph MacOS Playbook
        B[playbooks/macos.yml]:::playbook
    end

    subgraph Roles
        D[elliotweiser.osx-command-line-tools]:::role
        E[geerlingguy.mac.homebrew]:::role
        F[geerlingguy.mac.mas]:::role
        G[geerlingguy.mac.dock]:::role
    end

    subgraph Main Tasks
        C[roles/main/tasks/main.yml]:::task
    end

    subgraph Specific Tasks
        H[node.yml]:::task
        I[pyenv.yml]:::task
        J[tailscale.yml]:::task
        K[xcode.yml]:::task
        L[firewall.yml]:::task
        M[monitoring.yml]:::task
    end

    subgraph Handlers and Variables
        R[roles/main/handlers/main.yml]:::handlers
    end

    subgraph Templates
        T[roles/main/templates/*.j2]:::handlers
    end

    O --> A
    P --> A
    Q --> A

    A --> B
    A --> C

    B --> D
    B --> E
    B --> F
    B --> G

    C --> H
    C --> I
    C --> J
    C --> K
    C --> L
    C --> M

    R --> C
    T --> C
```

## Workflow Explanation

1. **Configuration Files**:

   - `default.config.yml` and `config.yml`: Define variables and settings.
   - `inventory`: Specifies target machines (e.g., b3) for the Ansible playbook.

2. **Main Playbook**:

   - `main.yml`: The entry point that orchestrates the entire process.

3. **MacOS Playbook**:

   - `playbooks/macos.yml`: Applies macOS-specific configurations.

4. **Roles**:

   - External roles for command-line tools, Homebrew, Mac App Store, and Dock configuration.

5. **Main Tasks**:

   - `roles/main/tasks/main.yml`: Central task file that imports specific tasks.

6. **Specific Tasks**:

   - Individual task files for different aspects of system configuration (node, pyenv, tailscale, etc.).

7. **Handlers and Variables**:

   - `roles/main/handlers/main.yml`: Defines handlers that can be called by tasks.

8. **Templates**:
   - Jinja2 templates used to generate configuration files on the target machine.

This improved diagram provides a clearer visual representation of your Ansible project's structure and workflow, with distinct sections and color-coding for different types of components.
