import ipaddress

from resources import colors

text: object = colors.TextColors

FULL_MASK: list[int] = [255, 255, 255, 255]
class Segments:

    def __init__(self, init_ip: str, hosts: list[int]) -> None:
        self.init_ip = ipaddress.IPv4Address(init_ip)
        self.hosts: list[int] = hosts
        self.bits:list[int] = []
        self.segment: dict = {
            'Host solicitados': None,
            'Host encontrados': None,
            'Dirección de red': None,
            'Máscara digital': None,
            'Máscara decimal': None,
            'Máscara wildcard': None,
            'Primera Ip utilizable': None,
            'Última Ip utilizable': None,
            'Dirección de BR': None
        }
        self.total_segments = 0

    def get_total_segments(self) -> int:
        return self.total_segments

    def add_segment(self) -> None:
        self.total_segments += 1

    def next_segment(self, mask: int) -> None:
        # Dirección de red del segmento
        network = ipaddress.IPv4Network((self.init_ip, mask), strict=False)
        self.segment.update({'Dirección de red': network})
        self.segment.update({'Máscara decimal': network.netmask})

        # Dirección Broadcast
        br_address = network.broadcast_address
        self.segment.update({'Dirección de BR': br_address})

        # Primera y última IP u ltilizable
        first_ip = network.network_address + 1
        self.segment.update({'Primera Ip utilizable': first_ip})
        last_ip = br_address - 1
        self.segment.update({'Última Ip utilizable': last_ip})
        octet_mask: list[int] = [int(octet) for octet in str(network.netmask).split(".")]

        wildcard_mask = self.set_wildcard_mask(octet_mask)
        self.segment.update({'Máscara wildcard': wildcard_mask})

        self.init_ip += 2**(32 - mask)
        return

    def set_mask(self, host: int) -> int:
        # Máscara de subred
        host_bits: int = host.bit_length() # Número de bits para representarse así mismo en binario
        mask: int = 32 - host_bits
        # host disponibles dentro del segmento
        usable_hosts: int = 2**(32 - mask) - 2
        # Asegura que los host solicitados no superen a los disponibles
        if usable_hosts < host:
            mask -= 1
            usable_hosts = 2**(32 - mask) - 2

        self.segment.update({'Host solicitados': host})
        self.segment.update({'Host encontrados': usable_hosts})
        return mask

    # Retorna la wildcard del segmento actual
    def set_wildcard_mask(self, mask: list[int]) -> str:
        wildcard_mask: list[int] = []
        for i in range(len(FULL_MASK)):
            # Calcula la Wildcard restando 255.255.255.255 con la máscara del segmento actual
            wildcard_mask.append(FULL_MASK[i] - mask[i])
        wildcard_mask = '.'.join(str(octet) for octet in wildcard_mask)
        return wildcard_mask

    def host_bits(self, mask: int) -> None:
        # limpia los bits de la lista para el siguiente segmento
        self.bits.clear()
        # Cqntidad de bits activos por segmento
        active_bits: int = 8 - (32 - mask)
        # Agrege los bits activos '1' y los inactivos '0'
        for _ in range(8):
            if active_bits > 0:
                self.bits.append(1)
                active_bits -= 1
            else:
                self.bits.append(0)

        digital_mask: str = ''.join(map(str,self.bits)) + "=/" + str(mask)
        self.segment.update({'Máscara digital': digital_mask})
        return

    def get_network_info(self) -> None:
        for key, value in self.segment.items():
            print(f"{key:.<30}{text.yellow}{value}{text.reset}")

    def export_network_info(self) -> list:
        return list(map(str, self.segment.values()))