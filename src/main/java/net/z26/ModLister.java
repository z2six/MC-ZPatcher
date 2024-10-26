package net.z26;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.Gson;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class ModLister {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.exit(1);
        }

        File modFolder = new File(args[0]);
        if (!modFolder.exists() || !modFolder.isDirectory()) {
            System.exit(1);
        }

        // Create temporary folder to store mod info and images
        File tempFolder = new File("mod_temp_data");
        if (!tempFolder.exists() && !tempFolder.mkdir()) {
            System.exit(1);
        }

        List<JsonObject> modInfoList = getModInfo(modFolder, tempFolder);

        // Write the mod info to a JSON file
        writeModInfoToJson(modInfoList, tempFolder);
    }

    private static List<JsonObject> getModInfo(File modFolder, File tempFolder) {
        List<JsonObject> modInfoList = new ArrayList<>();

        // Process both .jar and .jar.disabled files
        File[] modFiles = modFolder.listFiles((_, name) -> name.endsWith(".jar") || name.endsWith(".jar.disabled"));
        if (modFiles != null) {
            for (File modFile : modFiles) {
                try (ZipFile zipFile = new ZipFile(modFile)) {
                    ZipEntry jsonEntry = zipFile.getEntry("fabric.mod.json");

                    if (jsonEntry != null) {
                        InputStreamReader reader = new InputStreamReader(zipFile.getInputStream(jsonEntry));
                        JsonObject jsonObject = JsonParser.parseReader(reader).getAsJsonObject();

                        // Create a new JsonObject to store mod information
                        JsonObject modInfo = new JsonObject();

                        // Add custom fields at the start of the JsonObject
                        modInfo.addProperty("unique_id", UUID.randomUUID().toString());  // Unique identifier
                        modInfo.addProperty("curseforge_project_id", "");  // Placeholder for CurseForge project ID
                        modInfo.addProperty("curseforge_slug", "");  // Placeholder for CurseForge project ID
                        modInfo.addProperty("modrinth_project_id", "");   // Placeholder for Modrinth project ID

                        // Extract all fields dynamically from fabric.mod.json
                        for (Map.Entry<String, JsonElement> entry : jsonObject.entrySet()) {
                            modInfo.add(entry.getKey(), entry.getValue());
                        }

                        // Add mod file-specific information
                        boolean isEnabled = modFile.getName().endsWith(".jar");
                        modInfo.addProperty("enabled", isEnabled);  // Store enabled status
                        modInfo.addProperty("file_path", modFile.getAbsolutePath());  // File path

                        // Handle extracting the icon
                        String iconPath = jsonObject.has("icon") ? jsonObject.get("icon").getAsString() : null;
                        String extractedIconPath = extractIcon(zipFile, iconPath, modInfo.get("id").getAsString(), tempFolder);
                        modInfo.addProperty("icon_path", extractedIconPath);

                        // Add the completed mod info to the list
                        modInfoList.add(modInfo);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }

        return modInfoList;
    }

    private static String extractIcon(ZipFile zipFile, String iconPath, String modId, File tempFolder) {
        if (iconPath == null || iconPath.isEmpty()) {
            return null;  // No icon to extract
        }

        try {
            ZipEntry iconEntry = zipFile.getEntry(iconPath.replace("\\", "/")); // Ensure cross-platform path handling
            if (iconEntry != null) {
                File iconFile = new File(tempFolder, modId + ".png");
                try (InputStream inputStream = zipFile.getInputStream(iconEntry);
                     FileOutputStream outputStream = new FileOutputStream(iconFile)) {

                    byte[] buffer = new byte[1024];
                    int length;
                    while ((length = inputStream.read(buffer)) > 0) {
                        outputStream.write(buffer, 0, length);
                    }

                    return iconFile.getAbsolutePath();
                }
            }
        } catch (Exception e) {
            // Error handling for icon extraction
        }

        return null;
    }

    private static void writeModInfoToJson(List<JsonObject> modInfoList, File tempFolder) {
        Gson gson = new Gson();
        File jsonFile = new File(tempFolder, "mod_data.json");

        try (FileWriter writer = new FileWriter(jsonFile)) {
            gson.toJson(modInfoList, writer);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
