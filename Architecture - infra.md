flowchart TD
    %% Données sources
    subgraph SourceData [Sources de données]
        SQLDB[(Azure SQL / Base relationnelle)]
        ExcelFiles[(Fichiers Excel)]
        PDFDocs[(Documents PDF)]
        WebSources[(Sites Web)]
    end

    %% Ingestion et transformation
    subgraph Ingestion [Ingestion & ETL]
        ADF[Azure Data Factory / Pipelines]
        BlobStore[(Azure Blob Storage)]
        DataLake[(Azure Data Lake / Synapse)]
    end

    %% Indexation RAG
    subgraph RAGIndexing [Index RAG & Vector Store]
        Embeddings[(Vectorisation / Embeddings)]
        VectorStore[(Azure AI Search Index)]
    end

    %% LLM et Conversation
    subgraph ChatOps [Couche Conversationnelle]
        ChatAPI[(API Chat / Web App)]
        ContextLayer[(Gestion du contexte)]
        LLM[Azure OpenAI (LLM)]
    end

    %% Auth & Observabilité
    subgraph Infra [Sécurité & Monitoring]
        EntraID[(Microsoft Entra ID)]
        Monitor[(Azure Monitor / App Insights)]
    end

    %% BI & Analytique
    subgraph Analytics [Dashboards & BI]
        PowerBI[(Power BI / Synapse Analytics)]
    end

    %% Liens de flux

    %% Source -> Ingestion
    SQLDB --> ADF
    ExcelFiles --> ADF
    PDFDocs --> ADF
    WebSources --> ADF

    %% Ingestion -> Stockage
    ADF --> BlobStore
    ADF --> DataLake

    %% Stockage -> RAG Indexing
    BlobStore --> Embeddings
    DataLake --> Embeddings
    Embeddings --> VectorStore

    %% RAG & Conversation
    VectorStore --> LLM
    ChatAPI --> ContextLayer
    ContextLayer --> LLM

    %% Auth & Monitoring
    ChatAPI --> EntraID
    ChatAPI --> Monitor
    LLM --> Monitor
    VectorStore --> Monitor

    %% BI / Analytique
    DataLake --> PowerBI
