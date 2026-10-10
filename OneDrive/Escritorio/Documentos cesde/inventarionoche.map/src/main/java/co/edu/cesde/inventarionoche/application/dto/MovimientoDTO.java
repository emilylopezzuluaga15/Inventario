package co.edu.cesde.inventarionoche.application.dto;

import co.edu.cesde.inventarionoche.domain.model.TipoMovimiento;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MovimientoDTO {

    private Long id;

    @NotNull(message = "Falta el producto")
    private ProductoDTO producto;

    @NotNull(message = "Falta la cantidad")
    @Min(value = 1, message = "La cantidad tiene que ser mínimo 1")
    private Integer cantidad;

    @NotNull(message = "Falta el tipo de movimiento (ENTRADA o SALIDA)")
    private TipoMovimiento tipo;
}
