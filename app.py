import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:google_generative_ai/google_generative_ai.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:permission_handler/permission_handler.dart';

// గమనిక: మీ Gemini API Key ఇక్కడ నమోదు చేయండి
const String geminiApiKey = "AQ.Ab8RN6IELJB2yhussCFa7xQXyAQf1U6VGs3xDlCn22nX5Ve-GA";

void main() {
  runApp(const LegalAssistantApp());
}

class LegalAssistantApp extends StatelessWidget {
  const LegalAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BNS Legal Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _textController = TextEditingController();
  final ImagePicker _picker = ImagePicker();
  late stt.SpeechToText _speech;
  
  bool _isListening = false;
  bool _isLoading = false;
  File? _selectedImage;
  String _analysisResult = "";

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
  }

  // మైక్రోఫోన్ ద్వారా తెలుగు/ఇంగ్లీష్ వాయిస్ తీసుకోవడం
  Future<void> _listenVoice() async {
    var status = await Permission.microphone.request();
    if (status.isGranted) {
      if (!_isListening) {
        bool available = await _speech.initialize(
          onStatus: (val) {
            if (val == 'done' || val == 'notListening') {
              setState(() => _isListening = false);
            }
          },
          onError: (val) => setState(() => _isListening = false),
        );
        if (available) {
          setState(() => _isListening = true);
          _speech.listen(
            onResult: (val) {
              setState(() {
                _textController.text = val.recognizedWords;
              });
            },
            localeId: "te_IN", // తెలుగు వాయిస్ సపోర్ట్
          );
        }
      } else {
        setState(() => _isListening = false);
        _speech.stop();
      }
    }
  }

  // కెమెరా లేదా గ్యాలరీ నుండి ఫోటో ఎంచుకోవడం
  Future<void> _pickImage(ImageSource source) async {
    if (source == ImageSource.camera) {
      await Permission.camera.request();
    }
    final XFile? photo = await _picker.pickImage(source: source, imageQuality: 85);
    if (photo != null) {
      setState(() {
        _selectedImage = File(photo.path);
      });
    }
  }

  // Gemini API ద్వారా BNS / BNSS / BSA లీగల్ అనాలిసిస్
  Future<void> _analyzeCase() async {
    if (_textController.text.trim().isEmpty && _selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("దయచేసి కేస్ వివరాలు రాయండి, మాట్లాడండి లేదా ఫోటో అప్‌లోడ్ చేయండి.")),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _analysisResult = "";
    });

    try {
      final model = GenerativeModel(
        model: 'gemini-2.5-flash',
        apiKey: geminiApiKey,
      );

      final prompt = """
      You are an expert Indian Criminal Law Investigation Assistant strictly following the new criminal laws:
      1. Bharatiya Nyaya Sanhita (BNS)
      2. Bharatiya Nagarik Suraksha Sanhita (BNSS)
      3. Bharatiya Sakshya Adhiniyam (BSA)

      Case Input / Complaint text:
      "${_textController.text}"

      Generate a comprehensive investigation advisory covering:
      - **Applicable BNS Sections & Punishments** (Include IPC equivalents for easy reference)
      - **Applicable BNSS Procedures** (Arrest guidelines, Section 35(3) notices, search/seizure, forensic mandatory visit under Section 176(3))
      - **Evidence Collection under BSA** (Physical, ocular, digital/electronic evidence guidelines & Section 63 certificate)
      - **Step-by-Step IO Investigation SOP** (Sequential action plan from FIR to Final Report)

      Format the response in clear, structured Telugu with English legal terms in parentheses.
      """;

      final List<Content> contentList = [];
      
      if (_selectedImage != null) {
        final imageBytes = await _selectedImage!.readAsBytes();
        contentList.add(
          Content.multi([
            TextPart(prompt),
            DataPart('image/jpeg', imageBytes),
          ]),
        );
      } else {
        contentList.add(Content.text(prompt));
      }

      final response = await model.generateContent(contentList);

      setState(() {
        _analysisResult = response.text ?? "విశ్లేషణ పూర్తి చేయడంలో లోపం సంభవించింది.";
      });
    } catch (e) {
      setState(() {
        _analysisResult = "Error: $e\n\nదయచేసి API Key సరిగ్గా ఉందో లేదో సరిచూసుకోండి.";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('⚖️ BNS / BNSS Legal Assistant', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Text & Voice Input Box
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  children: [
                    TextField(
                      controller: _textController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        hintText: "ఫిర్యాదు వివరాలు నమోదు చేయండి లేదా మైక్ ద్వారా మాట్లాడండి...",
                        border: InputBorder.none,
                      ),
                    ),
                    const Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            IconButton(
                              icon: const Icon(Icons.camera_alt, color: Colors.indigo),
                              tooltip: "కెమెరా ద్వారా ఫోటో తీయండి",
                              onPressed: () => _pickImage(ImageSource.camera),
                            ),
                            IconButton(
                              icon: const Icon(Icons.photo_library, color: Colors.indigo),
                              tooltip: "గ్యాలరీ నుండి ఎంచుకోండి",
                              onPressed: () => _pickImage(ImageSource.gallery),
                            ),
                          ],
                        ),
                        IconButton(
                          icon: Icon(
                            _isListening ? Icons.mic : Icons.mic_none,
                            color: _isListening ? Colors.red : Colors.indigo,
                            size: 30,
                          ),
                          tooltip: "వాయిస్ టైపింగ్",
                          onPressed: _listenVoice,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),

            // ఎంచుకున్న ఇమేజ్ ప్రివ్యూ
            if (_selectedImage != null) ...[
              Stack(
                alignment: Alignment.topRight,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.file(_selectedImage!, height: 160, width: double.infinity, fit: BoxFit.cover),
                  ),
                  IconButton(
                    icon: const Icon(Icons.cancel, color: Colors.red),
                    onPressed: () => setState(() => _selectedImage = null),
                  ),
                ],
              ),
              const SizedBox(height: 10),
            ],

            // Submit Button
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _analyzeCase,
              icon: _isLoading 
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.gavel),
              label: Text(_isLoading ? "విశ్లేషిస్తోంది..." : "కేస్ విశ్లేషించండి (Generate SOP)", style: const TextStyle(fontSize: 16)),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.indigo,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 20),

            // ఫలితాల డిస్‌ప్లే
            if (_analysisResult.isNotEmpty) ...[
              const Text("📋 లీగల్ విశ్లేషణ & దర్యాప్తు నివేదిక:", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: MarkdownBody(
                  data: _analysisResult,
                  selectable: true,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
