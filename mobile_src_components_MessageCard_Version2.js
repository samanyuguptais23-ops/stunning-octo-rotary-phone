import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { COLORS, FONT, SPACING } from "../theme";

export function MessageCard({ item, onPlay }) {
  return (
    <View style={styles.card}>
      <Text style={styles.type}>{item.type?.toUpperCase()}</Text>
      {item.content ? <Text style={styles.content}>{item.content}</Text> : null}

      {item.audio_url ? (
        <TouchableOpacity onPress={() => onPlay(item.audio_url)}>
          <Text style={styles.play}>▶ Play Voice Note</Text>
        </TouchableOpacity>
      ) : null}

      <Text style={styles.meta}>{item.sender_name || "Unknown"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.yellow,
    padding: SPACING.md,
    borderRadius: 12,
    marginVertical: SPACING.xs
  },
  type: {
    fontWeight: "800",
    marginBottom: 4
  },
  content: {
    fontSize: FONT.normal
  },
  play: {
    marginTop: SPACING.sm,
    fontSize: FONT.normal,
    fontWeight: "700"
  },
  meta: {
    fontSize: FONT.small,
    marginTop: 6
  }
});