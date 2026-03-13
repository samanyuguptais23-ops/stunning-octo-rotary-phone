import React, { useEffect, useState } from "react";
import { View, Text, TextInput, FlatList, StyleSheet, Alert } from "react-native";
import { Audio } from "expo-av";
import { COLORS, SPACING, FONT } from "../theme";
import { BigButton } from "../components/BigButton";
import { StatusPill } from "../components/StatusPill";
import { MessageCard } from "../components/MessageCard";
import { getDeviceId } from "../utils/deviceId";
import { useMeshSocket } from "../hooks/useMeshSocket";
import { SERVER_URL } from "../config";

export default function HomeScreen() {
  const [deviceId, setDeviceId] = useState("");
  const [messages, setMessages] = useState([]);
  const [name, setName] = useState("Anonymous");
  const [updateText, setUpdateText] = useState("");
  const [haveText, setHaveText] = useState("");
  const [needText, setNeedText] = useState("");

  const [recording, setRecording] = useState(null);

  useEffect(() => {
    getDeviceId().then(setDeviceId);
  }, []);

  const { connected } = useMeshSocket(deviceId, (msg) => {
    if (msg?.id) {
      setMessages((prev) => [msg, ...prev].slice(0, 200));
    }
  });

  useEffect(() => {
    fetch(`${SERVER_URL}/messages`)
      .then((r) => r.json())
      .then((data) => setMessages(data.reverse()))
      .catch(() => {});
  }, []);

  const sendMessage = async (type = "general", priority = 4, content = "", audio_url = "") => {
    await fetch(`${SERVER_URL}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type,
        priority,
        content,
        sender: deviceId,
        sender_name: name,
        audio_url
      })
    });
  };

  const postText = async (type = "general", priority = 4) => {
    if (!updateText.trim()) return;
    await sendMessage(type, priority, updateText.trim());
    setUpdateText("");
  };

  const postResource = async () => {
    if (!haveText.trim() && !needText.trim()) return;
    const content = `HAS: ${haveText || "—"} | NEEDS: ${needText || "—"}`;
    await sendMessage("resource", 3, content);
    setHaveText("");
    setNeedText("");
  };

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission needed", "Microphone permission is required.");
        return;
      }
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
    } catch (err) {
      Alert.alert("Error", "Recording failed.");
    }
  };

  const stopRecording = async () => {
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);

      const form = new FormData();
      form.append("file", {
        uri,
        name: "voice.m4a",
        type: "audio/m4a"
      });

      const res = await fetch(`${SERVER_URL}/audio`, {
        method: "POST",
        body: form
      });
      const data = await res.json();
      await sendMessage("voice", 2, "", data.url);
    } catch {
      Alert.alert("Error", "Failed to send voice note.");
    }
  };

  const playAudio = async (audioUrl) => {
    const { sound } = await Audio.Sound.createAsync({ uri: `${SERVER_URL}${audioUrl}` });
    await sound.playAsync();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>PulseLink</Text>
      <Text style={styles.subtitle}>Disaster Communication</Text>
      <StatusPill connected={connected} />

      <Text style={styles.label}>Your Name</Text>
      <TextInput style={styles.input} value={name} onChangeText={setName} />

      <Text style={styles.label}>Quick Update</Text>
      <TextInput
        style={styles.input}
        value={updateText}
        onChangeText={setUpdateText}
        placeholder="Type a short message…"
      />

      <BigButton label="SEND UPDATE" onPress={() => postText("general", 4)} />
      <BigButton label="SEND SOS" color={COLORS.danger} onPress={() => postText("sos", 1)} />

      <Text style={styles.label}>Walkie‑Talkie (Hold to Talk)</Text>
      <BigButton
        label={recording ? "RECORDING..." : "PRESS & HOLD TO TALK"}
        color={COLORS.yellowDark}
        onPress={() => {}}
        onLongPress={startRecording}
        onPressOut={recording ? stopRecording : undefined}
      />

      <Text style={styles.label}>Resource Board</Text>
      <TextInput style={styles.input} value={haveText} onChangeText={setHaveText} placeholder="I HAVE…" />
      <TextInput style={styles.input} value={needText} onChangeText={setNeedText} placeholder="I NEED…" />
      <BigButton label="POST RESOURCE" onPress={postResource} />

      <Text style={styles.label}>Latest Messages</Text>
      <FlatList
        data={messages}
        keyExtractor={(item, idx) => item.id || idx.toString()}
        renderItem={({ item }) => <MessageCard item={item} onPlay={playAudio} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.white, padding: SPACING.lg },
  title: { fontSize: 32, fontWeight: "800", color: COLORS.text },
  subtitle: { fontSize: FONT.normal, marginBottom: SPACING.md },
  label: { fontSize: FONT.normal, marginTop: SPACING.md, marginBottom: SPACING.sm, fontWeight: "600" },
  input: {
    borderWidth: 1,
    borderColor: COLORS.gray,
    borderRadius: 12,
    padding: SPACING.md,
    fontSize: FONT.normal
  }
});