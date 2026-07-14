import { Alert, Button, Chip, Paper, Stack, Typography } from "@mui/material";
import { isAxiosError } from "axios";
import { useState } from "react";

import type { RecipeNote, RecipeNoteWriteInput } from "../api/recipeApi";
import {
  useCreateRecipeNote,
  useDeleteRecipeNote,
  useUpdateRecipeNote,
} from "../hooks/useRecipeMutations";
import RecipeNoteDialog from "./RecipeNoteDialog";

const noteTypeLabels: Record<string, string> = {
  cooking_tip: "Приготовление",
  expedition_tip: "Поход",
  serving_tip: "Подача",
};

function getApiErrorMessage(error: unknown): string {
  if (isAxiosError<{ error?: string }>(error)) {
    return error.response?.data?.error ?? "Не удалось сохранить заметку.";
  }
  return "Не удалось сохранить заметку.";
}

interface RecipeNotesSectionProps {
  recipeId: string;
  notes: RecipeNote[];
}

export default function RecipeNotesSection({ recipeId, notes }: RecipeNotesSectionProps) {
  const createMutation = useCreateRecipeNote();
  const updateMutation = useUpdateRecipeNote();
  const deleteMutation = useDeleteRecipeNote();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingNote, setEditingNote] = useState<RecipeNote | null>(null);
  const [dialogError, setDialogError] = useState<string | null>(null);
  const activeMutation = editingNote ? updateMutation : createMutation;

  const openCreate = () => {
    setEditingNote(null);
    setDialogError(null);
    createMutation.reset();
    setDialogOpen(true);
  };

  const openEdit = (note: RecipeNote) => {
    setEditingNote(note);
    setDialogError(null);
    updateMutation.reset();
    setDialogOpen(true);
  };

  const submit = async (input: RecipeNoteWriteInput) => {
    setDialogError(null);
    try {
      if (editingNote) {
        await updateMutation.mutateAsync({ recipeId, noteId: editingNote.id, input });
      } else {
        await createMutation.mutateAsync({ recipeId, input });
      }
      setDialogOpen(false);
      setEditingNote(null);
    } catch (error) {
      setDialogError(getApiErrorMessage(error));
    }
  };

  const remove = async (note: RecipeNote) => {
    if (!window.confirm("Удалить эту заметку?")) {
      return;
    }
    await deleteMutation.mutateAsync({ recipeId, noteId: note.id });
  };

  return (
    <Stack spacing={1.5}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={2}
        justifyContent="space-between"
        alignItems={{ xs: "stretch", sm: "center" }}
      >
        <Typography variant="h6">Заметки</Typography>
        <Button size="small" variant="contained" onClick={openCreate}>
          Добавить заметку
        </Button>
      </Stack>

      {deleteMutation.isError && (
        <Alert severity="error">{getApiErrorMessage(deleteMutation.error)}</Alert>
      )}

      {notes.length === 0 ? (
        <Typography color="text.secondary">Заметок пока нет.</Typography>
      ) : (
        notes.map((note) => (
          <Paper key={note.id} variant="outlined" sx={{ p: 2 }}>
            <Stack spacing={1.5}>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip size="small" label={noteTypeLabels[note.type] ?? note.type} />
                <Chip size="small" variant="outlined" label={`Приоритет ${note.priority}`} />
              </Stack>
              <Typography>{note.text}</Typography>
              <Stack direction="row" spacing={1} justifyContent="flex-end">
                <Button size="small" onClick={() => openEdit(note)}>Изменить</Button>
                <Button
                  size="small"
                  color="error"
                  disabled={deleteMutation.isPending}
                  onClick={() => void remove(note)}
                >
                  Удалить
                </Button>
              </Stack>
            </Stack>
          </Paper>
        ))
      )}

      <RecipeNoteDialog
        open={dialogOpen}
        note={editingNote}
        isSubmitting={activeMutation.isPending}
        errorMessage={dialogError}
        onClose={() => {
          setDialogOpen(false);
          setEditingNote(null);
        }}
        onSubmit={(input) => void submit(input)}
      />
    </Stack>
  );
}
