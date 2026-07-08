import { Alert } from "@mui/material";

interface Props {
  message?: string;
}

export default function ErrorMessage({ message = "Something went wrong" }: Props) {
  return <Alert severity="error">{message}</Alert>;
}
