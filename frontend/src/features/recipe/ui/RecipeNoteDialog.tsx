import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

import type { RecipeNote } from "../api/recipeApi";
import {
  toRecipeNoteWriteInput,
  validateRecipeNoteDraft,
  type RecipeNoteDraft,
} from "../model/recipeNotesProducts";

const initialDraft: RecipeNoteDraft = {
  type: "cooking_tip",
  text: "",
  priority: "100",
};

interface RecipeNoteDialogProps {
  open: boolean;
  note: RecipeNote | null;
  isSubmitting: boolean;
  errorMessage: string | null;
  onClose: () => void;
  onSubmit: (input: ReturnType<typeof toRecipeNoteWriteInput>) => void;
}

export default function RecipeNoteDialog({
  open,
  note,
  isSubmitting,
  errorMessage,
  onClose,
  onSubmit,
}: RecipeNoteDialogProps) {
  const [draft, setDraft] = useState<RecipeNoteDraft>(initialDraft);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    setValidationError(null);
    setDraft(
      note
        ? {
            type: note.type as RecipeNoteDraft["type"],
            text: note.text,
            priority: String(note.priority),
          }
        : initialDraft,
    );
  }, [note, open]);

  const handleSubmit = () => {
    const error = validateRecipeNoteDraft(draft);
    setValidationError(error);
    if (!error) {
      onSubmit(toRecipeNoteWriteInput(draft));
    }
  };

  return (
    <Dialog open={open} onClose={isSubmitting ? undefined : onClose} fullWidth maxWidth="sm">
      <DialogTitle>{note ? "Редактировать заметку" : "Добавить заметку"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          {(validationError || errorMessage) && (
            <Alert severity="error">{validationError ?? errorMessage}</Alert>
          )}
          <FormControl fullWidth>
            <InputLabel id="recipe-note-type-label">Тип заметки</InputLabel>
            <Select
              labelId="recipe-note-type-label"
              label="Тип заметки"
              value={draft.type}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  type: event.target.value as RecipeNoteDraft["type"],
                }))
              }
            >
              <MenuItem value="cooking_tip">Совет по приготовлению</MenuItem>
              <MenuItem value="expedition_tip">Походный совет</MenuItem>
              <MenuItem value="serving_tip">Совет по подаче</MenuItem>
            </Select>
          </FormControl>
          <TextField
            label="Текст"
            value={draft.text}
            onChange={(event) =>
              setDraft((current) => ({ ...current, text: event.target.value }))
            }
            multiline
            minRows={4}
            fullWidth
          />
          <TextField
            label="Приоритет"
            type="number"
            value={draft.priority}
            onChange={(event) =>
              setDraft((current) => ({ ...current, priority: event.target.value }))
            }
            inputProps={{ min: 0 }}
            helperText="Меньшее число показывается выше."
            fullWidth
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>Отмена</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isSubmitting}>
          {isSubmitting ? "Сохранение…" : "Сохранить"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
