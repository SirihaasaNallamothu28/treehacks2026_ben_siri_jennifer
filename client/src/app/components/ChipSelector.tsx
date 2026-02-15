import { useState } from "react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Input } from "./ui/input";
import { Plus } from "lucide-react";

interface ChipSelectorProps {
  label: string;
  options: string[];
  multiSelect?: boolean;
  onSelectionChange?: (selected: string[]) => void;
}

export function ChipSelector({ 
  label, 
  options, 
  multiSelect = true,
  onSelectionChange 
}: ChipSelectorProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const [customItems, setCustomItems] = useState<string[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [customInput, setCustomInput] = useState("");

  const handleToggle = (option: string) => {
    let newSelected: string[];
    if (multiSelect) {
      newSelected = selected.includes(option)
        ? selected.filter((item) => item !== option)
        : [...selected, option];
    } else {
      newSelected = selected.includes(option) ? [] : [option];
    }
    setSelected(newSelected);
    onSelectionChange?.(newSelected);
  };

  const handleAddCustom = () => {
    if (customInput.trim()) {
      const newCustom = [...customItems, customInput.trim()];
      setCustomItems(newCustom);
      
      const newSelected = [...selected, customInput.trim()];
      setSelected(newSelected);
      onSelectionChange?.(newSelected);
      
      setCustomInput("");
      setIsDialogOpen(false);
    }
  };

  const handleRemoveCustom = (item: string) => {
    setCustomItems(customItems.filter((i) => i !== item));
    handleToggle(item);
  };

  // Filter out "Other" from the main options
  const regularOptions = options.filter((option) => option !== "Other");
  const hasOtherOption = options.includes("Other");

  return (
    <div className="space-y-4">
      <p className="text-lg">{label}</p>
      <div className="space-y-3">
        {/* Regular chips */}
        <div className="flex flex-wrap gap-2">
          {regularOptions.map((option) => (
            <Badge
              key={option}
              variant={selected.includes(option) ? "default" : "outline"}
              className="cursor-pointer px-4 py-2 transition-all hover:scale-105"
              onClick={() => handleToggle(option)}
            >
              {option}
            </Badge>
          ))}
          
          {/* Custom added items */}
          {customItems.map((item) => (
            <Badge
              key={item}
              variant={selected.includes(item) ? "default" : "outline"}
              className="cursor-pointer px-4 py-2 transition-all hover:scale-105"
              onClick={() => handleRemoveCustom(item)}
            >
              {item} ✕
            </Badge>
          ))}
        </div>

        {/* Centered "+ Other" button below */}
        {hasOtherOption && (
          <div className="flex justify-center pt-2">
            <Button
              variant="outline"
              size="icon"
              className="rounded-full w-10 h-10 border-2 border-dashed hover:bg-[#00b4d8]/10 hover:border-[#0077b6] hover:text-[#0077b6] transition-all"
              onClick={() => setIsDialogOpen(true)}
            >
              <Plus className="h-5 w-5" />
            </Button>
          </div>
        )}
      </div>

      {/* Custom Input Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Custom Option</DialogTitle>
            <DialogDescription>
              Enter your own interest or strength that's not listed.
            </DialogDescription>
          </DialogHeader>
          <Input
            placeholder="Type here..."
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleAddCustom();
              }
            }}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddCustom}>Add</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}