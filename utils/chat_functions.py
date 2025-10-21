# utils/chat_functions.py
import os
import json
import streamlit as st
from openai import OpenAI

# ──────────────────────────────────────────────────────────────────────────────
# Utilidades para hacer el código robusto a distintas versiones del SDK
# ──────────────────────────────────────────────────────────────────────────────
def _vector_store_iface(client):
    """
    Devuelve el 'namespace' que contiene los métodos de vector stores, ya sea:
        - client.beta.vector_stores
        - client.vector_stores
    Si no existe en tu SDK, devuelve None.
    """
    beta = getattr(client, "beta", None)
    if beta is not None and hasattr(beta, "vector_stores"):
        return client.beta.vector_stores
    if hasattr(client, "vector_stores"):
        return client.vector_stores
    return None


def _create_vector_store(client, name: str):
    vs = _vector_store_iface(client)
    if vs is None:
        raise AttributeError(
            "Este SDK de 'openai' no tiene API de vector stores. "
            "Actualiza con: pip install -U openai  (y usa 'from openai import OpenAI')."
        )
    return vs.create(name=name)


def _retrieve_vector_store(client, vector_store_id: str):
    vs = _vector_store_iface(client)
    if vs is None:
        raise AttributeError(
            "Este SDK de 'openai' no tiene API de vector stores. "
            "Actualiza con: pip install -U openai"
        )
    return vs.retrieve(vector_store_id)


def _upload_files_to_vector_store(client, vector_store_id: str, file_paths):
    """
    Sube archivos al vector store usando la API disponible.
    En SDKs recientes existe: client.beta.vector_stores.file_batches.upload_and_poll
    Si estás en el namespace sin 'beta', asumimos análogo: client.vector_stores.file_batches.upload_and_poll
    """
    # Detecta el namespace correcto
    vs_ns = None
    beta = getattr(client, "beta", None)
    if beta is not None and hasattr(beta, "vector_stores"):
        vs_ns = client.beta.vector_stores
    elif hasattr(client, "vector_stores"):
        vs_ns = client.vector_stores

    if vs_ns is None or not hasattr(vs_ns, "file_batches"):
        raise AttributeError(
            "Tu SDK no expone 'file_batches.upload_and_poll' para vector stores. "
            "Actualiza el paquete 'openai'."
        )

    file_streams = [open(p, "rb") for p in file_paths]
    try:
        file_batch = vs_ns.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=file_streams,
        )
        return file_batch
    finally:
        for fs in file_streams:
            try:
                fs.close()
            except Exception:
                pass


# ──────────────────────────────────────────────────────────────────────────────
# App principal: QA del paper con Assistant + File Search
# ──────────────────────────────────────────────────────────────────────────────
def chat_paper_AI(
    api_key=st.secrets.get("gpt_key"),
    local_file_path="paper.pdf",
    vector_store_id_path="vector_store_id.json",
    file_id_path="file_id.json",
):
    # Permite fallback al entorno si no viene en secrets
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)

    st.markdown(
        "### Query system for the paper "
        "[Non-Overlapping Arrangement of Identical Objects: An insight for molecular close packing]"
        "(https://doi.org/10.26434/chemrxiv-2024-sm9rp)"
    )
    st.markdown("Examples:")
    info1, info2, info3 = st.columns(3)
    with info1:
        st.info("What are the main findings?")
        st.info("what are the conclusions?")
    with info2:
        st.info("Why is this paper important?")
        st.info("Explain figure 2")
    with info3:
        st.info("Explain the methodology")
        st.info("what are the future directions?")

    # ── helpers de persistencia ────────────────────────────────────────────────
    def save_vector_store_id(vsid):
        with open(vector_store_id_path, "w") as f:
            json.dump({"vector_store_id": vsid}, f)

    def load_vector_store_id():
        if os.path.exists(vector_store_id_path):
            with open(vector_store_id_path, "r") as f:
                return json.load(f).get("vector_store_id")
        return None

    def save_file_id(fid):
        with open(file_id_path, "w") as f:
            json.dump({"file_id": fid}, f)

    def load_file_id():
        if os.path.exists(file_id_path):
            with open(file_id_path, "r") as f:
                return json.load(f).get("file_id")
        return None

    vector_store_id = load_vector_store_id()
    file_id = load_file_id()

    # ── Vector store: crear o recuperar ───────────────────────────────────────
    if vector_store_id is None:
        with st.spinner("Creating vector store..."):
            vector_store = _create_vector_store(client, name="Paper")
            vector_store_id = vector_store.id
            save_vector_store_id(vector_store_id)
    else:
        with st.spinner("Using existing vector store..."):
            vector_store = _retrieve_vector_store(client, vector_store_id)

    # ── Subir y procesar PDF si aún no se sube ────────────────────────────────
    if file_id is None:
        if os.path.exists(local_file_path):
            with st.spinner("Uploading files and polling status..."):
                file_batch = _upload_files_to_vector_store(
                    client, vector_store_id, [local_file_path]
                )
            st.success("Files uploaded and processed successfully!")
            st.write(f"Status: {getattr(file_batch, 'status', 'unknown')}")
            st.write(f"File counts: {getattr(file_batch, 'file_counts', {})}")

            with st.spinner("Uploading file to assistant..."):
                message_file = client.files.create(
                    file=open(local_file_path, "rb"), purpose="assistants"
                )
                file_id = message_file.id
                save_file_id(file_id)
        else:
            st.error(
                "The file 'paper.pdf' does not exist. Please make sure the file is in the correct location."
            )
            return
    else:
        # Log liviano en consola
        print("Document ready.")

    # ── Crear Assistant y vincular vector store ───────────────────────────────
    with st.spinner("Creating assistant..."):
        paper_assistant = client.beta.assistants.create(
            name="Paper Assistant",
            instructions=(
                "You are an author of a research paper. "
                "Write latex formulas only using double $$ symbols. "
                "Example $$d_{\\text{max}} = x_2(y) - x_1(y)$$. "
                "Using \\[ \\] or \\( \\) is forbidden. "
                "Use your knowledge base to answer questions about the paper."
            ),
            model="gpt-3.5-turbo",
            tools=[{"type": "file_search"}],
        )

        paper_assistant = client.beta.assistants.update(
            assistant_id=paper_assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        )

    # ── UI de consulta ────────────────────────────────────────────────────────
    ask = st.chat_input("Ask something about the paper")
    if not ask:
        return

    with st.spinner("Processing your request..."):
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": ask,
                    "attachments": [{"file_id": file_id, "tools": [{"type": "file_search"}]}],
                }
            ]
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=paper_assistant.id,
            instructions="Please address the user as reader.",
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            def extract_text(sync_cursor_page):
                for msg in getattr(sync_cursor_page, "data", []):
                    for block in getattr(msg, "content", []):
                        if getattr(block, "type", None) == "text":
                            return block.text.value
                return "No text found."

            value = extract_text(messages)
            st.write(value)
            print(value)
        else:
            st.warning(f"Run status: {run.status}")
