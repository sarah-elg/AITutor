
def get_css_styles():
    return f"""
    <style>
    {get_tab_styles()}
    {get_button_styles()}
    {get_input_styles()}
    {get_checkbox_styles()}
    {get_example_styles()}
    </style>
    """

def get_tab_styles():
    """Stile für Tabs"""
    return """
button.selected[role="tab"][aria-selected="true"] {
        background: #005CA9 !important;
        color: #fff !important;
        border-radius: 12px 12px 0 0 !important;
        border: 2px solid #005CA9 !important;
        font-weight: bold !important;
        box-shadow: 0 2px 8px #005ca93a;
        border-bottom: none !important;
        position: relative;
    }
    button.selected[role="tab"][aria-selected="true"]::after {
        content: none !important;
        display: none !important;
        background: none !important;
        border: none !important;
    }
    button[role="tab"]:not(.selected)[aria-selected="false"] {
        background: #E6F0FA !important;
        color: #005CA9 !important;
        border-radius: 12px 12px 0 0 !important;
        border: 2px solid #E6F0FA !important;
        margin-right: 4px !important;
        font-weight: normal !important;
    }
    button[role="tab"] {
        font-size: 1.1em !important;
        padding: 8px 24px !important;
    }
    
    label[for="range_id_0"],
    label[for="range_id_1"] {
        background: transparent !important;
        color: #666 !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: normal !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    label[for="range_id_0"] span,
    label[for="range_id_1"] span {
        color: #666 !important;
    }

    label.container.show_textbox_border {
        background: transparent !important;
        color: #666 !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: normal !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    label.container.show_textbox_border span {
        color: #666 !important;
    }
    """

def get_button_styles():
    """Stile für Buttons"""
    return """
button.primary, button[variant="primary"] {
        background: #005CA9 !important;
        color: #fff !important;
        border: 2px solid #005CA9 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px #005ca93a;
        transition: background 0.2s, color 0.2s;
    }
    button.primary:hover, button[variant="primary"]:hover {
        background: #003366 !important;
        border-color: #003366 !important;
    }
    button:not(.primary):not([variant="primary"]) {
        background: #E6F0FA !important;
        color: #005CA9 !important;
        border: 2px solid #E6F0FA !important;
        font-weight: normal !important;
        border-radius: 10px !important;
    }
    input[type="range"]::-webkit-slider-thumb {
        background: #005CA9 !important; /* Uni-Blau für den Thumb */
        border: 2px solid #005CA9 !important;
    }
    input[type="range"]::-webkit-slider-runnable-track {
        background: #E6F0FA !important;
        height: 8px !important;
        border-radius: 4px !important;
    }
    input[type="range"]::-webkit-slider-thumb {
        z-index: 2;
        position: relative;
    }
    input[type="range"]::-webkit-slider-runnable-track {
        background: linear-gradient(
            to right,
            #003366 0%,
            #003366 var(--range_progress, 50%),
            #E6F0FA var(--range_progress, 50%),
            #E6F0FA 100%
        ) !important;
    }

    input[type="range"]::-moz-range-thumb {
        background: #005CA9 !important;
        border: 2px solid #005CA9 !important;
    }
    input[type="range"]::-moz-range-progress {
        background-color: #003366 !important; 
        height: 8px !important;
    }
    input[type="range"]::-moz-range-track {
        background-color: #E6F0FA !important;
        height: 8px !important;
    }

    input[type="range"]::-ms-fill-lower {
        background: #003366 !important;
        border-radius: 4px !important;
    }
    input[type="range"]::-ms-fill-upper {
        background: #E6F0FA !important;
        border-radius: 4px !important;
    }
    """

def get_input_styles():
    """Stile für Eingabefelder"""
    return """
    label.selected {
        background: #005CA9 !important;
        color: #fff !important;
        border-color: #005CA9 !important;
        font-weight: bold !important;
    }

   label.selected span {
        color: #fff !important;
    }

    label {
        background: #E6F0FA !important;
        color: #005CA9 !important;
        border: 2px solid #E6F0FA !important;
        border-radius: 8px !important;
        padding: 6px 16px !important;
        margin-right: 8px !important;
        font-weight: normal !important;
        cursor: pointer;
        transition: background 0.2s, color 0.2s;

    input[type="radio"]:checked + label {
        color: #fff !important;
        background: #005CA9 !important;
        border-color: #005CA9 !important;
        font-weight: bold !important;
        }

    input[type="radio"] + label:hover {
        background: #cce0f7 !important;
    }

    input[type="radio"] {
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        width: 0;
        height: 0;
        margin: 0;
        padding: 0;
        border: none;
        position: absolute;
        left: -9999px;
    }

    .svelte-1cl284s {
        background: #005CA9 !important;
    }

    input[type="range"]::-webkit-slider-runnable-track {
        background: #E6F0FA !important;
    }

    input[type="range"]::-webkit-slider-thumb {
        background: #005CA9 !important;
        border: 2px solid #005CA9 !important;
    }

    .svelte-1cl284s .fill {
        background: #005CA9 !important;
    }

    input[type="range"]::-moz-range-track {
        background: #E6F0FA !important;
    }

    input[type="range"]::-moz-range-thumb {
        background: #005CA9 !important;
        border: 2px solid #005CA9 !important;
    }

    input[type="range"]::-ms-track {
        background: #E6F0FA !important;
    }

    input[type="range"]::-ms-thumb {
        background: #005CA9 !important;
        border: 2px solid #005CA9 !important;
    }

    input[type="range"]::-ms-fill-lower {
        background: #005CA9 !important;
    }

    .gradio-slider .progress-bar {
        background: #005CA9 !important;
    }

    .gradio-slider .handle {
        background: #005CA9 !important;
        border-color: #005CA9 !important;
    }

    .svelte-1cl284s .thumb {
        background: #005CA9 !important;
    }

    .svelte-1cl284s .track {
        background: #E6F0FA !important;
    }

    .svelte-1cl284s .track-fill {
        background: #005CA9 !important;
    }

    input[type="radio"]:checked {
        accent-color: #005CA9 !important;
    }

    input[type="checkbox"]:checked {
        accent-color: #005CA9 !important;
    }
    """

def get_checkbox_styles():
    """Stile für Checkboxen"""
    return """
.gr-checkbox-group {
        display: flex !important;
        flex-direction: column !important;
    }

    .gr-checkbox-group label {
        display: block !important;
        margin-bottom: 8px !important;
        width: 100% !important;
    }

    input[type="checkbox"] + label {
        color: #005CA9 !important;
        background: #E6F0FA !important;
        border: 2px solid #E6F0FA !important;
        border-radius: 8px !important;
        padding: 6px 16px !important;
        margin-right: 8px !important;
        font-weight: normal !important;
        transition: background 0.2s, color 0.2s;
    }

    input[type="checkbox"]:checked + label {
        color: #fff !important;
        background: #005CA9 !important;
        border-color: #005CA9 !important;
        font-weight: bold !important;
    }

    input[type="checkbox"] {
        accent-color: #005CA9 !important;
    }

    .gr-check-radio {
        accent-color: #005CA9 !important;
    }

    .gr-check-radio:checked {
        background-color: #005CA9 !important;
        border-color: #005CA9 !important;
    }
    """

def get_example_styles():
    """Stile für Beispiele"""
    return """
.svelte-drgfj2 .example, .svelte-1ipelgc .example, .svelte-1tcem6n .example {
        background: #E6F0FA !important;
        color: #005CA9 !important;
        border: 1.5px solid #005CA9 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        transition: background 0.2s, color 0.2s;
    }

    .svelte-drgfj2 .example.selected,
    .svelte-1ipelgc .example.selected,
    .svelte-1tcem6n .example.selected,
    .svelte-drgfj2 .example:active,
    .svelte-1ipelgc .example:active,
    .svelte-1tcem6n .example:active {
        background: #005CA9 !important;
        color: #fff !important;
        border-color: #005CA9 !important;
    }
    """
