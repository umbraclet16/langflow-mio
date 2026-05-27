import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

export interface EmbeddingModelOption {
  id?: string;
  name: string;
  provider: string;
  icon?: string;
  metadata?: Record<string, unknown>;
}

export const useGetEmbeddingModelOptions: useQueryFunctionType<
  undefined,
  EmbeddingModelOption[]
> = (options) => {
  const { query } = UseRequestProcessor();

  const getEmbeddingModelOptionsFn = async (): Promise<
    EmbeddingModelOption[]
  > => {
    const response = await api.get<EmbeddingModelOption[]>(
      `${getURL("MODEL_OPTIONS")}/embedding`,
    );
    return response.data;
  };

  const queryResult = query(
    ["useGetEmbeddingModelOptions"],
    getEmbeddingModelOptionsFn,
    {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5, // 5 minutes
      ...options,
    },
  );

  return queryResult;
};
