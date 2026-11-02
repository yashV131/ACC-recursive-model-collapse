# Samarth Mathur
# code from the "Building Your First Demo" tutorial on the Gradio "Get Started" page

import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")
    
demo.launch(share=True)