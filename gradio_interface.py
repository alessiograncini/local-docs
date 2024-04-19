import gradio as gr
from data_preparation import data_prep
from qa_system import qna

# Gradio Interface for PDF Upload
pdf_upload_interface = gr.Interface(
    fn=data_prep,
    inputs=gr.File(label="Upload PDF"),
    outputs="text",
    allow_flagging="never"
)

# Gradio Interface for Chatbot
chatbot_interface = gr.Interface(
    fn=qna,
    inputs=gr.Textbox(label="Enter Your Question"),
    outputs=[
        gr.Textbox(label="Mistral Answer"),
        gr.Textbox(label="Retrieved Documents from MongoDB Atlas")
    ],
    allow_flagging="never"
)

# Combine interfaces into tabs
iface = gr.TabbedInterface(
    [pdf_upload_interface, chatbot_interface],
    ["Upload PDF", "Chatbot"]
)

# Launch the Gradio app
iface.launch()