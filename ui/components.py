import gradio as gr

def create_image_sources():
    """Create image source components"""
    with gr.Row(elem_classes="source-images"):
        columns = []
        for i in range(5):
            with gr.Column():
                image = gr.Image(label=f"Image Source {i+1}", type="pil", elem_classes="image-container")
                caption = gr.Textbox(label="Details", show_label=True, elem_classes="source-caption")
                columns.append((image, caption))
    return columns

def create_text_sources():
    """Create text source components"""
    with gr.Row(elem_classes="source-images"):
        columns = []
        for i in range(5):
            with gr.Column():
                image = gr.Image(label=f"Text Source {i+1}", type="pil", elem_classes="image-container")
                caption = gr.Textbox(label="Details", show_label=True, elem_classes="source-caption")
                columns.append((image, caption))
    return columns

def create_results_table():
    """Create results table component"""
    return gr.Dataframe(
        headers=['Source', 'Product ID', 'Name', 'Rating', 'Price'],
        row_count=10,
        col_count=(5,5),
        interactive=False,
        elem_classes="results-table",
        column_widths=['100px', '300px', '300px', '100px', '100px']
    ) 