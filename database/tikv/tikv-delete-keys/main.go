package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"github.com/tikv/client-go/v2/txnkv"
	"os"
	"strings"
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

	// Delete all keys
	if err := deleteAllKeys(client); err != nil {
		fmt.Println("Failed to delete all keys:", err)
		return
	}

	fmt.Println("Successfully deleted all keys from TiKV")
}

// deleteAllKeys removes all keys from TiKV
func deleteAllKeys(client *txnkv.Client) error {
	fmt.Println("Starting to delete all keys from TiKV...")

	// Begin a transaction for scanning keys
	scanTxn, err := client.Begin()
	if err != nil {
		return fmt.Errorf("failed to begin scan transaction: %w", err)
	}

	// Create an iterator starting from empty byte array to scan all keys
	iter, err := scanTxn.Iter([]byte{}, nil)
	if err != nil {
		scanTxn.Rollback()
		return fmt.Errorf("error creating iterator: %w", err)
	}
	defer iter.Close()

	// Collect all keys to delete
	var keysToDelete [][]byte
	for iter.Valid() {
		key := iter.Key()
		// Make a copy of the key since iter.Key() returns a reference that may be invalid after iter.Next()
		keyCopy := make([]byte, len(key))
		copy(keyCopy, key)
		keysToDelete = append(keysToDelete, keyCopy)

		if err := iter.Next(); err != nil {
			scanTxn.Rollback()
			return fmt.Errorf("error iterating: %w", err)
		}
	}

	// We can now discard the scan transaction
	if err := scanTxn.Rollback(); err != nil {
		fmt.Println("Warning: Failed to rollback scan transaction:", err)
	}

	// If there are no keys, we're done
	if len(keysToDelete) == 0 {
		fmt.Println("No keys found in TiKV")
		return nil
	}

	fmt.Printf("Found %d keys to delete\n", len(keysToDelete))

	// For better performance with many keys, delete in batches
	batchSize := 1000
	for i := 0; i < len(keysToDelete); i += batchSize {
		end := i + batchSize
		if end > len(keysToDelete) {
			end = len(keysToDelete)
		}

		batch := keysToDelete[i:end]

		// Begin a transaction for deleting this batch of keys
		deleteTxn, err := client.Begin()
		if err != nil {
			return fmt.Errorf("failed to begin delete transaction: %w", err)
		}

		for _, key := range batch {
			if err := deleteTxn.Delete(key); err != nil {
				deleteTxn.Rollback()
				return fmt.Errorf("failed to delete key: %w", err)
			}
		}

		// Commit the transaction
		if err := deleteTxn.Commit(context.Background()); err != nil {
			deleteTxn.Rollback()
			return fmt.Errorf("failed to commit delete transaction: %w", err)
		}

		fmt.Printf("Deleted keys %d to %d\n", i+1, end)
	}

	return nil
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
