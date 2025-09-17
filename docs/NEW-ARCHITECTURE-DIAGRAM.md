# New Multi-Agent Architecture Diagram

*Updated for the new production-ready architecture - September 16, 2025*

## 🎬 Complete Video Production Pipeline

```mermaid
graph TD
    A[User Input: Topic] --> B[Orchestrator Agent]
    B --> C[Full Script Writer - FSW]
    C --> D[High-Level Story Structure]
    D --> E{Schema Validation}
    
    E -->|PASS| F[Scene Script Writer - SSW]
    E -->|WARN| F
    
    F --> G[Scene 1 Package]
    F --> H[Scene 2 Package]
    F --> I[Scene N Package]
    
    G --> J{Scene Schema Validation}
    H --> K{Scene Schema Validation}
    I --> L{Scene Schema Validation}
    
    J -->|PASS| M[Image Create Agent - ICA]
    K -->|PASS| M
    L -->|PASS| M
    
    M --> N[Frame 1A, 1B, ...]
    M --> O[Frame 2A, 2B, ...]
    M --> P[Frame NA, NB, ...]
    
    N --> Q[Image Assets]
    O --> Q
    P --> Q
    
    Q --> R[Build Report & Final Assembly]
    R --> S[Complete Video Package]
    
    style C fill:#e3f2fd
    style F fill:#fff3e0
    style M fill:#e8f5e8
    style B fill:#f3e5f5
    style E fill:#ffeb3b
    style J fill:#ffeb3b
    style K fill:#ffeb3b
    style L fill:#ffeb3b
```

## 🤖 Agent Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant FSW as Full Script Writer
    participant SSW as Scene Script Writer
    participant ICA as Image Create Agent
    participant SM as Session Manager
    
    U->>O: Topic + Preferences
    O->>SM: Create Session (YYYYMMDD-UUID)
    
    Note over O: Stage 1: High-Level Planning
    O->>FSW: Generate Story Structure
    FSW->>FSW: Apply Story Focus Engine
    FSW->>FSW: Validate with Story Validator
    FSW->>O: FullScript.json
    O->>O: Schema Validation
    O->>SM: Save full_script.json
    
    Note over O: Stage 2: Detailed Scene Scripts
    loop For Each Scene
        O->>SSW: Expand Scene Beat
        SSW->>SSW: Educational Enhancement
        SSW->>SSW: Generate Production Package
        SSW->>O: ScenePackage.json
        O->>O: Schema Validation
        O->>SM: Save scene_package_N.json
    end
    
    Note over O: Stage 3: Image Generation
    loop For Each Scene Package
        O->>ICA: Generate Scene Images
        loop For Each Visual Frame
            ICA->>ICA: Enhance Prompt + Character Consistency
            ICA->>ICA: Generate/Mock Image
            ICA->>SM: Save Image + Metadata
        end
        ICA->>O: ImageAsset[].json
    end
    
    Note over O: Stage 4: Final Assembly
    O->>SM: Save image_assets.json
    O->>SM: Save build_report.json
    O->>U: Complete Video Package
```

## 🏗️ New Architecture Components

```mermaid
graph TB
    subgraph "New Multi-Agent System"
        direction TB
        
        subgraph "Core Agents"
            FSW[Full Script Writer<br/>High-level story planning]
            SSW[Scene Script Writer<br/>Production-ready packages]
            ICA[Image Create Agent<br/>Visual asset generation]
            ORC[Orchestrator<br/>Pipeline management]
        end
        
        subgraph "JSON Schemas"
            FS[FullScript.json]
            SP[ScenePackage.json]
            IA[ImageAsset.json]
        end
        
        subgraph "Validation System"
            SV[Schema Validation]
            SF[Safety Checks]
            QC[Quality Control]
        end
        
        subgraph "Core Services"
            SM[Session Manager]
            SC[Shared Context]
            SE[Story Engine]
            EE[Educational Enhancer]
        end
    end
    
    FSW --> FS
    SSW --> SP
    ICA --> IA
    
    ORC --> FSW
    ORC --> SSW
    ORC --> ICA
    
    FSW --> SE
    SSW --> EE
    SSW --> SC
    ICA --> SM
    
    FS --> SV
    SP --> SV
    IA --> SV
    
    SV --> QC
    QC --> SF
    
    style FSW fill:#e3f2fd
    style SSW fill:#fff3e0
    style ICA fill:#e8f5e8
    style ORC fill:#f3e5f5
    style FS fill:#ffeb3b
    style SP fill:#ffeb3b
    style IA fill:#ffeb3b
```

## 📊 Data Flow & File Organization

```mermaid
graph LR
    subgraph "Input"
        T[Topic]
        P[Preferences]
    end
    
    subgraph "Processing"
        FSW[FSW] --> FS[full_script.json]
        SSW[SSW] --> SP1[scene_package_1.json]
        SSW --> SP2[scene_package_2.json]
        SSW --> SPN[scene_package_N.json]
        ICA[ICA] --> IA[image_assets.json]
    end
    
    subgraph "Assets"
        IMG1[1a.png, 1b.png, ...]
        IMG2[2a.png, 2b.png, ...]
        IMGN[Na.png, Nb.png, ...]
    end
    
    subgraph "Metadata"
        BR[build_report.json]
        META[metadata.json]
        PROMPTS[prompts/]
    end
    
    subgraph "Session: YYYYMMDD-UUID"
        FS --> SESSION
        SP1 --> SESSION
        SP2 --> SESSION
        SPN --> SESSION
        IA --> SESSION
        IMG1 --> SESSION
        IMG2 --> SESSION
        IMGN --> SESSION
        BR --> SESSION
        META --> SESSION
        PROMPTS --> SESSION
    end
    
    T --> FSW
    P --> FSW
    FS --> SSW
    SP1 --> ICA
    SP2 --> ICA
    SPN --> ICA
```

## 🔄 Legacy vs New Architecture Comparison

| Aspect | Legacy Architecture | New Architecture |
|--------|-------------------|------------------|
| **Agent Count** | 5 agents (mixed roles) | 4 agents (clear separation) |
| **Data Flow** | Implicit, mixed | Explicit JSON contracts |
| **Validation** | Basic | Multi-layer (Schema + Semantic + Safety) |
| **Output Quality** | Variable | Production-ready |
| **Scene Detail** | Basic dialogue + simple prompts | Rich packages with timing, TTS, continuity |
| **Image Generation** | 1 image per scene | 3-8 frames per scene |
| **File Organization** | Basic script.json | Comprehensive session structure |
| **Debugging** | Limited logging | Full prompt/response tracking |
| **Extensibility** | Monolithic | Modular, schema-driven |
