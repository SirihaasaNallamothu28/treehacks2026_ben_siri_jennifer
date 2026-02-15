import { useState, KeyboardEvent, ChangeEvent } from "react";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import { X } from "lucide-react";

interface SearchBarChipsProps {
  label: string;
  placeholder: string;
  onSelectionChange?: (selected: string[]) => void;
}

export function SearchBarChips({ 
  label, 
  placeholder,
  onSelectionChange 
}: SearchBarChipsProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState("");

  const addChip = (value: string) => {
    const trimmed = value.trim();
    if (trimmed && !selected.includes(trimmed)) {
      const newSelected = [...selected, trimmed];
      setSelected(newSelected);
      onSelectionChange?.(newSelected);
    }
  };

  const removeChip = (chipToRemove: string) => {
    const newSelected = selected.filter((item) => item !== chipToRemove);
    setSelected(newSelected);
    onSelectionChange?.(newSelected);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    
    // Check if user typed a comma
    if (value.includes(",")) {
      const parts = value.split(",");
      // Add all complete parts (before the last comma)
      for (let i = 0; i < parts.length - 1; i++) {
        addChip(parts[i]);
      }
      // Keep the part after the last comma in the input
      setInputValue(parts[parts.length - 1]);
    } else {
      setInputValue(value);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    // Handle backspace to remove last chip if input is empty
    if (e.key === "Backspace" && inputValue === "" && selected.length > 0) {
      removeChip(selected[selected.length - 1]);
    }
    
    // Handle Enter key
    if (e.key === "Enter" && inputValue.trim()) {
      e.preventDefault();
      addChip(inputValue);
      setInputValue("");
    }
  };

  return (
    <div className="space-y-3">
      <p className="text-lg">{label}</p>
      <div className="relative">
        {/* Container with border that looks like an input */}
        <div className="min-h-[44px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 transition-all">
          <div className="flex flex-wrap gap-2 items-center">
            {/* Selected chips */}
            {selected.map((chip) => (
              <Badge
                key={chip}
                variant="default"
                className="pl-3 pr-2 py-1 flex items-center gap-1"
              >
                <span>{chip}</span>
                <button
                  onClick={() => removeChip(chip)}
                  className="hover:bg-primary-foreground/20 rounded-full p-0.5 transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
            
            {/* Input field */}
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={selected.length === 0 ? placeholder : ""}
              className="flex-1 min-w-[120px] outline-none bg-transparent placeholder:text-muted-foreground"
            />
          </div>
        </div>
      </div>
    </div>
  );
}