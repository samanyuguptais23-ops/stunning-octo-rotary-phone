import AsyncStorage from "@react-native-async-storage/async-storage";

const KEY = "pulselink_device_id";

function makeId() {
  return "node_" + Math.random().toString(36).substring(2, 10);
}

export async function getDeviceId() {
  const existing = await AsyncStorage.getItem(KEY);
  if (existing) return existing;
  const id = makeId();
  await AsyncStorage.setItem(KEY, id);
  return id;
}