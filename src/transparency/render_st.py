import streamlit as st
from typing import Dict, Any, List
from .specs import METRIC_SPECS

class StreamlitRenderer:
    @staticmethod
    def render_transparency_expander(manifest: Dict[str, Any], metric_keys: List[str] = None):
        """
        Renders a Streamlit expander with transparency details for specific metrics.
        If metric_keys is None, renders all.
        """
        if not manifest:
            # Fallback if no manifest found, show generic specs?
            # Or just return
            st.info("No runtime manifest found for this date. Showing static specs.")
            params = {} # No runtime params
        else:
            params = manifest.get('parameters', {})

        with st.expander("🔍 Transparencia del Cálculo (Params & Supuestos)"):
            
            # Show Global Inputs if no specific metrics
            if not metric_keys:
                inputs = manifest.get('inputs', {}) if manifest else {}
                if inputs:
                    st.markdown(f"**Inputs Globales**: {inputs.get('tickers_count', 0)} Tickers procesados.")
            
            keys_to_show = metric_keys if metric_keys else METRIC_SPECS.keys()
            
            for key in keys_to_show:
                spec = METRIC_SPECS.get(key)
                if not spec:
                    continue
                
                st.markdown(f"#### {spec['name']}")
                st.markdown(f"_{spec['description']}_")
                
                # Runtime Params
                current_params = []
                for p_key in spec.get('params', []):
                    parts = p_key.split('.')
                    val = params
                    found = True
                    for part in parts:
                        if isinstance(val, dict) and part in val:
                            val = val[part]
                        else:
                            found = False
                            break
                    if found:
                        current_params.append(f"- `{parts[-1]}`: **{val}**")
                
                if current_params:
                    st.markdown("**Parámetros Efectivos (Run):**")
                    for p in current_params:
                        st.markdown(p)
                
                # Definitions & Assumptions
                tab1, tab2 = st.tabs(["Definición", "Supuestos"])
                with tab1:
                    st.markdown(spec.get('definition_md', ''))
                with tab2:
                    st.markdown(spec.get('assumptions_md', ''))
                
                if spec.get('references'):
                    st.markdown("**Referencias:**")
                    for text, link in spec['references']:
                        st.markdown(f"- [{text}]({link})")
                
                # --- NEW: Rich Detailed Manifest Data ---
                # Check if we have 'details' for this metric in the manifest
                # Structure: manifest['details'][key]
                details = manifest.get('details', {}).get(key)
                if details and key == 'market_mode':
                    st.divider()
                    st.markdown("### 🔬 Detalles de Cálculo (Market Mode)")
                    
                    if "error" in details:
                        st.error(f"Computation Info: {details['error']}")
                    else:
                        # 1. Scalar Metrics
                        meta = details.get('meta', {})
                        metrics = details.get('metrics', {})
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Ventana", f"{meta.get('window_days')}d")
                        m2.metric("N Activos", meta.get('n_assets_effective'))
                        m3.metric("Lambda1 Norm", f"{metrics.get('lambda1_norm',0):.2f}")
                        m4.metric("Explained Var", f"{metrics.get('explained_ratio',0):.1%}")
                        
                        st.caption(f"Periodo: {meta.get('window_start')} - {meta.get('window_end')}")

                        # 2. Assets Table
                        with st.expander("📋 Assets Usados / Excluidos", expanded=False):
                            assets = details.get('assets', [])
                            if assets:
                                df_assets = pd.DataFrame(assets)
                                st.dataframe(
                                    df_assets.style.applymap(lambda x: 'color: red' if not x else 'color: green', subset=['used']),
                                    use_container_width=True,
                                    hide_index=True
                                )
                        
                        # 3. Eigenvalues & Components
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Top Eigenvalues**")
                            eigs = details.get('eigenvalues', [])
                            if eigs:
                                st.dataframe(pd.DataFrame(eigs), hide_index=True)
                        
                        with c2:
                            st.markdown("**Top Eigenvector 1 Components**")
                            vecs = details.get('eigenvector_1', [])
                            if vecs:
                                df_vec = pd.DataFrame(vecs)
                                # Add color bar for weight?
                                st.dataframe(
                                    df_vec.style.background_gradient(subset=['weight'], cmap='coolwarm', vmin=-0.5, vmax=0.5),
                                    hide_index=True
                                )

                st.divider()
