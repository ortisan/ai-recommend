package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"github.com/tikv/client-go/v2/txnkv"
	"os"
	"strings"
	"time"
)

func main() {
	// Connect to PD endpoints from environment variable or use default
	pdEndpointsStr := os.Getenv("PD_ENDPOINTS")
	if pdEndpointsStr == "" {
		pdEndpointsStr = "127.0.0.1:2379"
	}
	pdEndpoints := strings.Split(pdEndpointsStr, ",")

	// Initialize client
	client, err := txnkv.NewClient(pdEndpoints)
	if err != nil {
		fmt.Println("Failed to create client:", err)
		return
	}
	defer func() {
		if err := client.Close(); err != nil {
			fmt.Println("Failed to close client:", err)
		}
	}()

	// Begin a transaction
	txn, err := client.Begin()
	if err != nil {
		fmt.Println("Failed to begin transaction:", err)
		return
	}

	// Put a key-value pair
	fmt.Println("Adding a test key-value pair...")
	key := []byte("!v")
	value := []byte("\u0000\u0002")

	err = txn.Set(key, value)
	if err != nil {
		fmt.Println("Failed to set key-value pair:", err)
		return
	}

	// Commit the transaction
	err = txn.Commit(context.Background())
	if err != nil {
		fmt.Println("Failed to commit transaction:", err)
		return
	}

	fmt.Println("Successfully added key-value pair to TiKV")
	fmt.Println("Key:", string(key))
	fmt.Println("Value:", string(value))

	// Begin another transaction for reading/exporting data
	txn, err = client.Begin()
	if err != nil {
		fmt.Println("Failed to begin transaction for reading:", err)
		return
	}

	fmt.Println("Scanning all keys and writing to JSON file...")

	// Create an iterator starting from empty byte array
	iter, err := txn.Iter([]byte{}, nil)
	if err != nil {
		fmt.Println("Error creating iterator:", err)
		return
	}
	defer iter.Close()

	// Map to store key-value pairs
	keyValueMap := make(map[string]interface{})

	// Iterate through all keys
	count := 0

	for iter.Valid() {
		key := iter.Key()
		value := iter.Value()

		// Create a unique, file-safe key name
		// First try as readable string
		keyStr := string(key)
		safeName := createSafeKeyName(keyStr)

		// Attempt to parse the value as JSON
		var parsedValue interface{}
		if err := json.Unmarshal(value, &parsedValue); err != nil {
			// If not valid JSON, store as string
			parsedValue = string(value)
		}

		// Store in map
		keyValueMap[safeName] = parsedValue

		err = iter.Next()
		if err != nil {
			fmt.Println("Error iterating:", err)
			break
		}

		count++
		// Optional: limit for testing
		if count >= 10000 {
			fmt.Println("Reached limit of 10000 keys, stopping iteration")
			break
		}
	}

	// Write the map to a JSON file
	outputDir := os.Getenv("OUTPUT_DIR")
	if outputDir == "" {
		outputDir = "."
	}

	// Create output directory if it doesn't exist
	fmt.Printf("Ensuring output directory exists: %s\n", outputDir)
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		fmt.Printf("Error creating output directory %s: %v\n", outputDir, err)
		return
	}

	outputFile := fmt.Sprintf("%s/tikv_keys.json", outputDir)
	fmt.Printf("Writing output to file: %s\n", outputFile)

	jsonData, err := json.MarshalIndent(keyValueMap, "", "  ")
	if err != nil {
		fmt.Println("Error marshaling to JSON:", err)
		return
	}

	err = os.WriteFile(outputFile, jsonData, 0644)
	if err != nil {
		fmt.Printf("Error writing to file %s: %v\n", outputFile, err)
		// Try to get more info about the directory
		if dirInfo, statErr := os.Stat(outputDir); statErr != nil {
			fmt.Printf("Error getting directory info: %v\n", statErr)
		} else {
			fmt.Printf("Directory exists: %v, Mode: %v\n", dirInfo.IsDir(), dirInfo.Mode())
		}
		return
	}

	fmt.Printf("Successfully wrote %d key-value pairs to %s\n", count, outputFile)

	// Sleep for debugging purposes if needed
	if os.Getenv("DEBUG_SLEEP") == "true" {
		fmt.Println("Sleeping for 60 minutes for troubleshooting...")
		sleepFor := 60 * 60 // 60 minutes in seconds
		time.Sleep(time.Duration(sleepFor) * time.Second)
	}
}

// createSafeKeyName generates a filename-safe representation of a key
func createSafeKeyName(key string) string {
	// If it's a printable string, clean it up for use as a key
	isPrintable := true
	for _, r := range key {
		if r < 32 || r > 126 {
			isPrintable = false
			break
		}
	}

	if isPrintable {
		// Replace characters that would be problematic in file names or JSON
		safe := strings.NewReplacer(
			"/", "_slash_",
			"\\", "_backslash_",
			":", "_colon_",
			"*", "_star_",
			"?", "_question_",
			"\"", "_quote_",
			"<", "_lt_",
			">", "_gt_",
			"|", "_pipe_",
			" ", "_space_",
		).Replace(key)

		// Truncate very long keys
		if len(safe) > 100 {
			safe = safe[:97] + "..."
		}

		return safe
	}

	// For binary data, use base64 encoding with a prefix
	return "binary_" + base64.StdEncoding.EncodeToString([]byte(key))
}
