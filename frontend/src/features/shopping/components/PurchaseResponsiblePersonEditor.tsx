import { Alert, Button, Stack, TextField, Typography } from "@mui/material";
import { FormEvent, useEffect, useState } from "react";

import { useUpdatePurchaseList } from "../hooks/usePurchaseList";
import {
  getResponsiblePersonSuccessMessage,
  isResponsiblePersonValid,
  normalizeResponsiblePerson,
  responsiblePersonMaxLength,
} from "../model/purchaseResponsiblePersonState";

interface Props {
  projectId: number;
  purchaseListId: string;
  responsiblePerson: string | null;
}

export default function PurchaseResponsiblePersonEditor({
  projectId,
  purchaseListId,
  responsiblePerson,
}: Props) {
  const [value, setValue] = useState(responsiblePerson ?? "");
  const [feedback, setFeedback] = useState<string>();
  const updateMutation = useUpdatePurchaseList(projectId);
  const isValid = isResponsiblePersonValid(value);
  const hasChanges = normalizeResponsiblePerson(value) !== responsiblePerson;

  useEffect(() => {
    setValue(responsiblePerson ?? "");
  }, [responsiblePerson]);

  async function save(nextValue: string) {
    if (!isResponsiblePersonValid(nextValue)) return;

    await updateMutation.mutateAsync({
      purchaseListId,
      input: { responsible_person: normalizeResponsiblePerson(nextValue) },
    });
    setFeedback(getResponsiblePersonSuccessMessage(nextValue));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback(undefined);
    await save(value);
  }

  async function handleClear() {
    setFeedback(undefined);
    setValue("");
    await save("");
  }

  return (
    <Stack component="form" spacing={1} onSubmit={handleSubmit}>
      <Typography variant="subtitle2">Ответственный за закупку</Typography>
      <TextField
        label="Имя"
        value={value}
        onChange={(event) => {
          setValue(event.target.value);
          setFeedback(undefined);
        }}
        size="small"
        fullWidth
        error={!isValid}
        helperText={
          isValid
            ? "Необязательное поле."
            : `Не более ${responsiblePersonMaxLength} символов.`
        }
        inputProps={{
          maxLength: responsiblePersonMaxLength,
          "aria-label": "Ответственный за закупку",
        }}
      />

      <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
        <Button
          type="submit"
          variant="contained"
          disabled={!isValid || !hasChanges || updateMutation.isPending}
        >
          Сохранить
        </Button>
        <Button
          type="button"
          variant="outlined"
          onClick={handleClear}
          disabled={updateMutation.isPending || value.length === 0}
        >
          Очистить
        </Button>
      </Stack>

      {updateMutation.isError ? (
        <Alert severity="error" role="alert">
          Не удалось сохранить ответственного за закупку.
        </Alert>
      ) : null}

      {feedback ? (
        <Alert severity="success" role="status">
          {feedback}
        </Alert>
      ) : null}
    </Stack>
  );
}
