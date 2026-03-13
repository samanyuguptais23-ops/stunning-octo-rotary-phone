import React from "react";
import { TouchableOpacity, Text, StyleSheet } from "react-native";
import { COLORS, FONT, SPACING } from "../theme";

export function BigButton({ label, color = COLORS.yellow, onPress, onLongPress }) {
  return (
    <TouchableOpacity
      style={[styles.btn, { backgroundColor: color }]}
      onPress={onPress}
      onLongPress={onLongPress}
    >
      <Text style={styles.text}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: {
    padding: SPACING.lg,
    borderRadius: 16,
    alignItems: "center",
    marginVertical: SPACING.sm
  },
  text: {
    fontSize: FONT.big,
    color: COLORS.text,
    fontWeight: "700"
  }
});