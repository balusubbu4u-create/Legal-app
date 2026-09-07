try:
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                config = types.GenerateContentConfig(
                    system_instruction=legal_system_instruction,
                    temperature=0.0,
                    top_p=0.95
                )

                content = []
                if uploaded_image:
                    content.append(uploaded_image)

                if case_text:
                    content.append(f"కేసు ఫిర్యాదు వివరాలు:\n{case_text}")
                else:
                    content.append("అప్‌లోడ్ చేసిన డాక్యుమెంట్ లేదా ఫోటోలోని వివరాలను చదివి పై నియమాల ప్రకారం విశ్లేషించండి.")

                # మొదట ప్రధాన మోడల్ రన్ చేయడం; 503 వస్తే బ్యాకప్ మోడల్ ట్రై చేయడం
                try:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=content,
                        config=config
                    )
                except Exception as model_err:
                    # 503 రద్దీ సమస్య వస్తే gemini-2.5-flash లేదా gemini-1.5-flash కి మారుతుంది
                    if "503" in str(model_err) or "UNAVAILABLE" in str(model_err):
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=content,
                            config=config
                        )
                    else:
                        raise model_err

                st.markdown("### 📋 దర్యాప్తు నివేదిక:")
                st.markdown(response.text)

            except Exception as e:
                if "503" in str(e):
                    st.error("గూగుల్ సర్వర్లలో ప్రస్తుతం రద్దీ ఎక్కువగా ఉంది. దయచేసి 1 నిమిషం తర్వాత మళ్లీ 'Analyze' బటన్ నొక్కండి.")
                else:
                    st.error(f"విశ్లేషణలో లోపం ఏర్పడింది: {e}")
