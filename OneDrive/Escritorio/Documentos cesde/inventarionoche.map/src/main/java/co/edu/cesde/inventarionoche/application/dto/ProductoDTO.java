package co.edu.cesde.inventarionoche.application.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProductoDTO {

    private Long id;

    @NotBlank(message = "Falta el nombre")
    @Size(max = 100, message = "El nombre no puede tener más de 100 letras")
    private String nombre;

    @Size(max = 255, message = "La descripción no puede tener más de 255 letras")
    private String descripcion;

    @NotNull(message = "Falta el precio")
    @PositiveOrZero(message = "El precio no puede ser negativo")
    private BigDecimal precio;

    @NotNull(message = "Falta el stock")
    @PositiveOrZero(message = "El stock no puede ser negativo")
    private Integer stock;
}
