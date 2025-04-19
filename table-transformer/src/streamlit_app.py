from table_creator.table_extractor import TableExtraction
import streamlit as st
import base64
from PIL import Image
import os
import cv2
import numpy as np
import tempfile
import traceback

# Load models only once
if 'tab_ext' not in st.session_state:
    st.session_state.tab_ext = TableExtraction()
    print('Models loaded.')


def process_image(imgpath):
    return st.session_state.tab_ext.detect(imgpath)

def draw_bounding_box(image, bbox):
    """Draw a bounding box on the image"""
    
    
    img_array = np.array(image)
    if len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    x_min, y_min, x_max, y_max = bbox
    cv2.rectangle(img_array, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    
    if len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    
    return Image.fromarray(img_array)


# Set page config
st.set_page_config(
    page_title="Table Extraction Tool",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded to show guide by default
)


# Enhanced CSS styling with updated upload section
st.markdown("""
    <style>
        /* Main container and background */
        .main { padding: 1.5rem; }
        .stApp { 
            background: linear-gradient(135deg, #f6f9fc 0%, #f0f4f8 100%);
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(90deg, #1a365d 0%, #2563eb 100%);
            color: white;
            padding: 2rem 3rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .main-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: white;
        }
        
        .main-header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Card containers */
        .content-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            margin-bottom: 1.5rem;
        }
        
        /* Upload section - Reduced size */
        .upload-section {
            text-align: center;
            padding: 1rem;
            border: 2px dashed #e5e7eb;
            border-radius: 12px;
            background-color: #f8fafc;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .upload-icon {
            font-size: 1.5rem;
            color: #2563eb;
            margin-bottom: 0.5rem;
        }
        
        /* Results section */
        .results-header {
            font-size: 1.25rem;
            color: #1f2937;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
        /* Download buttons */
        .download-button {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.2s;
            text-align: center;
            width: 100%;
        }
        
        .download-button:hover {
            background-color: #1d4ed8;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background-color: #f8fafc;
            padding: 0.5rem;
            border-radius: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #4b5563;
            font-weight: 500;
            padding: 0.5rem 1.5rem;
            border-radius: 6px;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #2563eb;
            color: white;
        }
            
        /* Guide section styling */
        .guide-section {
            background-color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }
        
        .guide-header {
            color: #1a365d;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }
        
        .guide-subheader {
            color: #2563eb;
            font-size: 1.2rem;
            margin: 1.5rem 0 0.5rem 0;
        }
        
        .guide-text {
            color: #4b5563;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        
        .feature-card {
            background-color: #f8fafc;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #2563eb;
        }
        
        .step-container {
            display: flex;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        
        .step-number {
            background-color: #2563eb;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            flex-shrink: 0;
        }
        
        .info-icon {
            color: #2563eb;
            margin-right: 0.5rem;
        }
        
        .tech-details {
            background-color: #f0f9ff;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

    </style>
""", unsafe_allow_html=True)



# Create sidebar with guide content
with st.sidebar:
    # st.markdown('<div class="guide-section">', unsafe_allow_html=True)
    st.divider()
    st.markdown('<h2 class="guide-header">📚 User Guide</h2>', unsafe_allow_html=True)
    
    # How It Works section
    st.markdown('<h3 class="guide-subheader">🎯 How It Works</h3>', unsafe_allow_html=True)
    st.markdown("""
        <div class="guide-text">
            This tool uses advanced computer vision and machine learning techniques to:
            <ul>
                <li>Detect and locate tables in document images</li>
                <li>Extract structured data from the detected tables</li>
                <li>Convert the data into easily manageable formats</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Usage Instructions
    st.markdown('<h3 class="guide-subheader">📝 Usage Instructions</h3>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="step-container">
            <div class="step-number">1</div>
            <div class="guide-text">Upload a document image containing a table (PNG, JPG, or JPEG format)</div>
        </div>
        
        <div class="step-container">
            <div class="step-number">2</div>
            <div class="guide-text">The tool will automatically detect and highlight the table in your image</div>
        </div>
        
        <div class="step-container">
            <div class="step-number">3</div>
            <div class="guide-text">View both raw and enhanced versions of the extracted data</div>
        </div>
        
        <div class="step-container">
            <div class="step-number">4</div>
            <div class="guide-text">Download the results in CSV format for further use</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Best Practices
    st.markdown('<h3 class="guide-subheader">💡 Best Practices</h3>', unsafe_allow_html=True)
    st.markdown("""
        <div class="feature-card">
            <strong>For Best Results:</strong>
            <ul>
                <li>Use clear, high-resolution images</li>
                <li>Ensure tables have well-defined borders</li>
                <li>Avoid skewed or rotated images</li>
                <li>Make sure text is clearly readable</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Technical Details (collapsible)
    with st.expander("🔧 Technical Details"):
        st.markdown("""
            <div class="tech-details">
                <p><strong>Algorithm Overview:</strong></p>
                <ul>
                    <li>Uses computer vision for table boundary detection</li>
                    <li>Employs OCR (Optical Character Recognition) for text extraction</li>
                    <li>Implements intelligent cell segmentation</li>
                    <li>Applies post-processing for enhanced accuracy</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Support Info
    st.markdown('<h3 class="guide-subheader">🔗 Connect with Me</h3>', unsafe_allow_html=True)
    st.markdown("""
        <div class="guide-text" style="font-size: 1rem;">
            If you encounter any issues or have questions, feel free to reach out:
            <a href="https://github.com/Sudhanshu1304" target="_blank" style="text-decoration: none;">
                <img src="https://img.icons8.com/ios-filled/20/000000/github.png" alt="GitHub" style="vertical-align: middle; margin-right: 5px;"/>
                GitHub
            </a> | 
            <a href="https://www.linkedin.com/in/sudhanshu-pandey-847448193/" target="_blank" style="text-decoration: none;">
                <img src="https://img.icons8.com/ios-filled/20/000000/linkedin.png" alt="LinkedIn" style="vertical-align: middle; margin-right: 5px;"/>
                LinkedIn
            </a> | 
            <a href="https://medium.com/@sudhanshu.dpandey" target="_blank" style="text-decoration: none;">
                <img src="https://img.icons8.com/ios-filled/20/000000/medium-logo.png" alt="Medium" style="vertical-align: middle; margin-right: 5px;"/>
                Medium
            </a>
        </div>
    """, unsafe_allow_html=True)

  

# Initialize session state for expanded view
if 'is_expanded' not in st.session_state:
    st.session_state.is_expanded = False


# Title and description
st.markdown("""
    <div class="main-header">
        <h1>📊 Table Extraction Tool</h1>
        <p>Upload an image containing tables and instantly convert them into structured data formats.</p>
    </div>
""", unsafe_allow_html=True)



# File upload section - Reduced size
# st.markdown('<div class="content-card">', unsafe_allow_html=True)
# st.markdown("""
#     <div class="upload-section">
#         <div class="upload-icon">📥</div>
#         <h3 style="font-size: 1.1rem; margin: 0.5rem 0;">Upload Table Image</h3>
#         <p style="font-size: 0.9rem; margin: 0;">Supported formats: PNG, JPG, JPEG</p>
#     </div>
# """, unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
st.markdown('</div>', unsafe_allow_html=True)

# Process the uploaded file
if uploaded_file is not None:
    with st.spinner('🔄 Processing your image...'):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        try:
            image = Image.open(uploaded_file)
            (raw_df, cleaned_df), bbox = process_image(temp_path)
            
            st.session_state.raw_data = raw_df
            st.session_state.processed_data = cleaned_df
            marked_image = draw_bounding_box(image, bbox[0])
            st.session_state.marked_image = marked_image
            
            # Side by side layout
            col1, col2 = st.columns([0.4, 0.6])
            
            with col1:
                # st.markdown('<div class="content-card image-container">', unsafe_allow_html=True)
                st.divider()
                st.markdown('<h3 class="results-header">Detected Table</h3>', unsafe_allow_html=True)
                st.image(marked_image, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.divider()
                st.markdown('<h3 class="results-header">Extracted Data</h3>', unsafe_allow_html=True)
                
                # # Toggle button for expanded view
                # if st.button("🔍 Toggle Full View" if not st.session_state.is_expanded else "⬆️ Collapse View"):
                #     st.session_state.is_expanded = not st.session_state.is_expanded
                
                tabs = st.tabs(["🔍 Raw Data", "✨ Enhanced Data ⭐"])
                
                with tabs[0]:
                    st.dataframe(st.session_state.raw_data, 
                               use_container_width=True,
                               height=600 if not st.session_state.is_expanded else None)
                
                    # Add HTML copy section for raw data
                    st.markdown("### 📋 Copy HTML Table")
                    html_raw = st.session_state.raw_data.to_html(index=False)
                    st.markdown("""
                        <div style="background-color: #f8fafc; padding: 0.5rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <p style="margin: 0; color: #475569; font-size: 0.9rem;">
                                ℹ️ This HTML can be copied and used directly in websites, LLM prompts, or other applications.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("""
                        <div style="max-height: 150px; overflow-y: auto; border-radius: 8px;">
                    """, unsafe_allow_html=True)
                    st.code(html_raw, language="html")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with tabs[1]:
                    st.markdown("""
                        <div style="background-color: #f0f9ff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                            <p style="margin: 0; color: #1e40af;">
                                ⭐ This is our enhanced version of the table with improved formatting and structure.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(st.session_state.processed_data, 
                               use_container_width=True,
                               height=600 if not st.session_state.is_expanded else None)
                    
                    # Add HTML copy section for enhanced data
                    st.markdown("### 📋 Copy HTML Table")
                    html_enhanced = st.session_state.processed_data.to_html(index=False)
                    st.markdown("""
                        <div style="background-color: #f8fafc; padding: 0.5rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <p style="margin: 0; color: #475569; font-size: 0.9rem;">
                                ℹ️ This HTML can be copied and used directly in websites, LLM prompts, or other applications.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("""
                        <div style="max-height: 150px; overflow-y: auto; border-radius: 8px;">
                    """, unsafe_allow_html=True)
                    st.code(html_enhanced, language="html")
                    st.markdown("</div>", unsafe_allow_html=True)

                # st.markdown('</div>', unsafe_allow_html=True)

            # Download section below both columns
            # st.markdown('<div class="content-card">', unsafe_allow_html=True)
            # Download section below both columns
            st.divider()
            st.markdown('<h3 class="results-header">Download Options</h3>', unsafe_allow_html=True)
            download_cols = st.columns([1, 0.1, 1])

            def get_csv_download_link(df, filename):
                csv = df.to_csv(index=False).encode()
                b64 = base64.b64encode(csv).decode()
                return f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-button">📥 Download {filename}</a>'

            with download_cols[0]:
                if 'raw_data' in st.session_state:
                    csv = st.session_state.raw_data.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Raw Data",
                        data=csv,
                        file_name="raw_data.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="raw_download"
                    )

            with download_cols[2]:
                if 'processed_data' in st.session_state:
                    csv = st.session_state.processed_data.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Enhanced Data ⭐",
                        data=csv,
                        file_name="enhanced_data.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="enhanced_download"
                    )
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error processing image: {str(traceback.format_exc())}")
        
        finally:
            try:
                os.unlink(temp_path)
            except Exception as e:
                st.warning(f"⚠️ Error removing temporary file: {str(e)}")
