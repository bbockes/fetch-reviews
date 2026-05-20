import { Button as ButtonPrimitive } from "@base-ui/react/button"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center border border-transparent bg-clip-padding text-sm font-medium whitespace-nowrap transition-all duration-200 outline-none select-none focus-visible:ring-3 focus-visible:ring-ring/40 active:not-aria-[haspopup]:scale-[0.98] disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default:
          "rounded-[20px] bg-foreground text-background hover:bg-foreground/90",
        outline:
          "rounded-full border-border bg-background text-foreground hover:bg-muted",
        secondary:
          "rounded-full bg-secondary text-secondary-foreground hover:bg-[#e0e0e0]",
        ghost:
          "rounded-full text-[#707070] hover:bg-muted hover:text-foreground",
        destructive:
          "rounded-[20px] bg-destructive/10 text-destructive hover:bg-destructive/20",
        link: "text-brand underline-offset-4 hover:text-foreground hover:underline",
        pill:
          "rounded-full bg-secondary px-6 py-2 text-base font-normal text-foreground hover:bg-[#e0e0e0]",
      },
      size: {
        default: "h-10 gap-1.5 px-5",
        xs: "h-7 gap-1 rounded-full px-3 text-xs",
        sm: "h-8 gap-1 rounded-full px-4 text-[0.8125rem]",
        lg: "h-12 gap-2 rounded-[20px] px-6 text-base",
        icon: "size-10 rounded-full",
        "icon-xs": "size-7 rounded-full [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8 rounded-full",
        "icon-lg": "size-12 rounded-full",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
