import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5000';

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${API_URL}/api/session`, { method: 'POST' })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Não foi possível iniciar o assistente.');
        return data;
      })
      .then((data) => setSessionId(data.session_id))
      .catch((requestError) => setError(requestError.message));
  }, []);

  async function sendMessage() {
    const text = message.trim();
    if (!text || !sessionId || loading) return;

    setMessage('');
    setError('');
    setMessages((current) => [...current, { id: `${Date.now()}-user`, role: 'user', text }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.details ? `${data.error} (${data.details})` : data.error || 'Erro ao consultar o assistente.');
      }
      setMessages((current) => [
        ...current,
        { id: `${Date.now()}-assistant`, role: 'assistant', text: data.response },
      ]);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.header}>
          <Text style={styles.eyebrow}>CARDIOIA</Text>
          <Text style={styles.title}>Seu cuidado começa pela conversa.</Text>
          <Text style={styles.subtitle}>Informação geral para acompanhar sua saúde cardiovascular.</Text>
        </View>

        <FlatList
          style={styles.chat}
          contentContainerStyle={styles.chatContent}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={[styles.bubble, item.role === 'user' ? styles.userBubble : styles.assistantBubble]}>
              <Text style={styles.bubbleLabel}>{item.role === 'user' ? 'VOCÊ' : 'CARDIOIA'}</Text>
              <Text style={[styles.bubbleText, item.role === 'user' && styles.userBubbleText]}>{item.text}</Text>
            </View>
          )}
          ListFooterComponent={loading ? <ActivityIndicator color="#e85d5d" style={styles.loader} /> : null}
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}
        <View style={styles.composerBlock}>
          <Text style={styles.inputLabel}>DIGITE SUA MENSAGEM</Text>
          <View style={styles.composer}>
            <TextInput
              style={styles.input}
              placeholder="Digite sua mensagem..."
              placeholderTextColor="#65727d"
              value={message}
              onChangeText={setMessage}
              onSubmitEditing={sendMessage}
              returnKeyType="send"
              editable={!loading}
              multiline={false}
            />
            <TouchableOpacity style={styles.sendButton} onPress={sendMessage} disabled={!sessionId || loading}>
              <Text style={styles.sendText}>ENVIAR</Text>
            </TouchableOpacity>
          </View>
        </View>
        <Text style={styles.disclaimer}>Este assistente não substitui avaliação de um profissional de saúde.</Text>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#f5f2ed' },
  container: { flex: 1, paddingHorizontal: 20 },
  header: { paddingTop: 24, paddingBottom: 18 },
  eyebrow: { color: '#e85d5d', fontSize: 12, fontWeight: '800', letterSpacing: 2 },
  title: { color: '#19232d', fontSize: 30, fontWeight: '800', marginTop: 8 },
  subtitle: { color: '#65727d', fontSize: 15, lineHeight: 21, marginTop: 8 },
  chat: { flex: 1 },
  chatContent: { gap: 12, paddingVertical: 10 },
  bubble: { borderRadius: 18, padding: 15, maxWidth: '88%' },
  assistantBubble: { alignSelf: 'flex-start', backgroundColor: '#ffffff' },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#19232d' },
  bubbleLabel: { color: '#e85d5d', fontSize: 10, fontWeight: '800', letterSpacing: 1, marginBottom: 6 },
  bubbleText: { color: '#19232d', fontSize: 16, lineHeight: 22 },
  userBubbleText: { color: '#ffffff' },
  loader: { marginVertical: 12 },
  error: { color: '#b33131', paddingVertical: 8 },
  composerBlock: { paddingTop: 8 },
  inputLabel: { color: '#65727d', fontSize: 10, fontWeight: '800', letterSpacing: 1, marginBottom: 6 },
  composer: { flexDirection: 'row', gap: 8, paddingVertical: 10 },
  input: { flex: 1, minHeight: 52, backgroundColor: '#ffffff', borderColor: '#c9d0d5', borderRadius: 14, borderWidth: 1, paddingHorizontal: 15, fontSize: 16, color: '#19232d' },
  sendButton: { backgroundColor: '#e85d5d', borderRadius: 14, justifyContent: 'center', paddingHorizontal: 14 },
  sendText: { color: '#ffffff', fontSize: 12, fontWeight: '800' },
  disclaimer: { color: '#84909c', fontSize: 11, lineHeight: 15, paddingBottom: 12, textAlign: 'center' },
});
