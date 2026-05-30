import { useTranslation } from "react-i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import {
  DEFAULT_BACK_LABEL,
  DEFAULT_HELP_LABEL,
  DEFAULT_NEXT_LABEL,
  DEFAULT_SUBMIT_LABEL,
} from "../constants";
import type { StepperModalFooterProps } from "../types";

export function StepperModalFooter({
  currentStep,
  totalSteps,
  onBack,
  onNext,
  onSubmit,
  nextDisabled = false,
  submitDisabled = false,
  isSubmitting = false,
  submitLabel,
  nextLabel,
  backLabel,
  helpHref,
  onHelp,
  helpLabel,
  submitTestId,
}: StepperModalFooterProps) {
  const { t } = useTranslation();
  const showHelp = helpHref || onHelp;

  const resolvedSubmitLabel =
    submitLabel ?? t("stepperModal.create", DEFAULT_SUBMIT_LABEL);
  const resolvedNextLabel =
    nextLabel ?? t("stepperModal.nextStep", DEFAULT_NEXT_LABEL);
  const resolvedBackLabel =
    backLabel ?? t("stepperModal.back", DEFAULT_BACK_LABEL);
  const resolvedHelpLabel =
    helpLabel ?? t("stepperModal.needHelp", DEFAULT_HELP_LABEL);

  return (
    <div className="flex w-full items-center justify-between">
      <div>
        {showHelp &&
          (helpHref ? (
            <Button
              variant="link"
              asChild
              className="px-2 text-muted-foreground"
            >
              <a
                href={helpHref}
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                {resolvedHelpLabel}
                <ForwardedIconComponent
                  name="ExternalLink"
                  className="ml-1 h-4 w-4"
                />
              </a>
            </Button>
          ) : (
            <Button variant="secondary" onClick={onHelp}>
              {resolvedHelpLabel}
            </Button>
          ))}
      </div>
      <div className="flex items-center gap-3">
        {currentStep > 1 && onBack && (
          <Button variant="outline" onClick={onBack}>
            {resolvedBackLabel}
          </Button>
        )}
        {currentStep < totalSteps ? (
          <Button onClick={onNext} disabled={nextDisabled}>
            {resolvedNextLabel}
          </Button>
        ) : (
          <Button
            onClick={onSubmit}
            disabled={submitDisabled || isSubmitting}
            data-testid={submitTestId}
          >
            {isSubmitting && (
              <ForwardedIconComponent
                name="Loader2"
                className="mr-2 h-4 w-4 animate-spin"
              />
            )}
            {resolvedSubmitLabel}
          </Button>
        )}
      </div>
    </div>
  );
}
