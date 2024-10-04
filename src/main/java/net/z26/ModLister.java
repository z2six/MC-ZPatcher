package net.z26;

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

public class ModLister {
    public static void main(String[] args) {
        if (args.length != 1) {
            //System.out.println("Usage: java ModLister <mod_folder>");
            System.exit(1);
        }

        File modFolder = new File(args[0]);
        if (!modFolder.exists() || !modFolder.isDirectory()) {
            //System.out.println("Invalid mod folder.");
            System.exit(1);
        }

        // Create temporary folder to store mod info and images
        File tempFolder = new File("mod_temp_data");
        if (!tempFolder.exists() && !tempFolder.mkdir()) {
            //System.out.println("Failed to create temp folder.");
            System.exit(1);
        }

        List<JsonObject> modInfoList = getModInfo(modFolder, tempFolder);

        // Write the mod info to a JSON file
        writeModInfoToJson(modInfoList, tempFolder);

        // Emit a message indicating where the mod data has been saved
        //System.out.println("Mod data extraction and icon generation completed.");
        //System.out.println("Data stored at: " + tempFolder.getAbsolutePath());
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

                        // Extract mod information
                        String modId = jsonObject.get("id").getAsString();
                        String modName = jsonObject.has("name") ? jsonObject.get("name").getAsString() : modId;
                        String version = jsonObject.has("version") ? jsonObject.get("version").getAsString() : "Unknown";
                        String description = jsonObject.has("description") ? jsonObject.get("description").getAsString() : "No description available.";
                        String authors = jsonObject.has("authors") ? jsonObject.get("authors").toString() : "No authors available.";
                        String contact = jsonObject.has("contact") ? jsonObject.get("contact").toString() : "No contact info available.";
                        boolean isEnabled = modFile.getName().endsWith(".jar");  // Check if mod is enabled

                        // Handle extracting the icon
                        String iconPath = jsonObject.has("icon") ? jsonObject.get("icon").getAsString() : null;
                        String extractedIconPath = extractIcon(zipFile, iconPath, modId, tempFolder);

                        // Create a JSON object for this mod's information
                        JsonObject modInfo = new JsonObject();
                        modInfo.addProperty("mod_id", modId);
                        modInfo.addProperty("mod_name", modName);
                        modInfo.addProperty("version", version);
                        modInfo.addProperty("description", description);
                        modInfo.addProperty("authors", authors);
                        modInfo.addProperty("contact", contact);
                        modInfo.addProperty("icon_path", extractedIconPath);
                        modInfo.addProperty("enabled", isEnabled);  // Store enabled status
                        modInfo.addProperty("modloader", "Fabric");  // Assuming all mods are Fabric for now

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
            //System.out.println("Error extracting icon for mod: " + modId);
        }

        return null;
    }

    private static void writeModInfoToJson(List<JsonObject> modInfoList, File tempFolder) {
        Gson gson = new Gson();
        File jsonFile = new File(tempFolder, "mod_data.json");

        try (FileWriter writer = new FileWriter(jsonFile)) {
            gson.toJson(modInfoList, writer);
            //System.out.println("Mod data written to: " + jsonFile.getAbsolutePath());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
