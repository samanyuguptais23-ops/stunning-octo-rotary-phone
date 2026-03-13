import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { COLORS, FONT, SPACING } from "../theme";

export function StatusPill({ connected }) {
  return (
    <View style={[styles.pill, { backgroundColor: connected ? COLORS.success : COLORS.danger }]}>
      <Text style={styles.text}>{connected ? "CONNECTED" : "OFFLINE"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    paddingVertical: SPACING.xs,
    paddingHorizontal: SPACING.md,
    borderRadius: 999
  },
  text: {
    color: COLORS.white,
    fontSize: FONT.small,
    fontWeight: "700"
  }
});