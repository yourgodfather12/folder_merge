## Prerequisites

- Python 3.x
- Tkinter library (usually included with Python installations)

## Usage

1. Run the script.
2. Click on the "Select Folder" button to choose the directory containing the folders you want to merge.
3. Once the folder is selected, click on the "Merge" button to start the merging process.
4. A progress bar will indicate the progress of the merging operation.
5. After the process completes, the merged folders will be available in the specified directory.

## Notes

- Ensure that the folders to be merged have a common base name followed by numerical suffixes (e.g., "Folder (1)", "Folder (2)", etc.).
- Only folders containing images or videos will be merged. Other files will be skipped.
- Empty folders will be deleted automatically after the merging process.

## Customization

- You can customize the appearance of the GUI by modifying the styles in the script.
- Adjust the resizing behavior by changing the divisor in the `resize_fonts` function to control text scaling.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
