package ai.trinetra.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import java.util.UUID;
import java.util.Map;

@Service
public class AuditService {

    private static final Logger log = LoggerFactory.getLogger(AuditService.class);

    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper;

    public AuditService(JdbcTemplate jdbcTemplate, ObjectMapper objectMapper) {
        this.jdbcTemplate = jdbcTemplate;
        this.objectMapper = objectMapper;
    }

    public void log(String entityType, UUID entityId, String action, 
                    String actorType, UUID actorId, 
                    Object oldState, Object newState, String ipAddress) {
        
        try {
            String oldStateJson = oldState != null ? objectMapper.writeValueAsString(oldState) : null;
            String newStateJson = newState != null ? objectMapper.writeValueAsString(newState) : null;

            jdbcTemplate.update(
                "INSERT INTO audit_log (entity_type, entity_id, action, actor_type, actor_id, old_state, new_state, ip_address) " +
                "VALUES (?, ?, ?, ?, ?, ?::jsonb, ?::jsonb, ?::inet)",
                entityType, entityId, action, actorType, actorId, oldStateJson, newStateJson, ipAddress
            );
        } catch (Exception e) {
            log.error("Failed to log audit event", e);
        }
    }
}
